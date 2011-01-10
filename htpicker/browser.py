#!/usr/bin/env python

import functools
import gtk
import logging
import urlparse
import webkit

class HTPickerWebView(webkit.WebView):
    def __init__(self, url=None, content=None):
        """content arg is a tuple: (content, mime_type, encoding, base_uri)"""
        super(HTPickerWebView, self).__init__()

        self.url = url
        self.content = content

        settings_values = (
            ("enable-default-context-menu",           False, '1.1.18'),
            ("enable-java-applet",                    False, '1.1.22'),
            ("enable-plugins",                        False, '???'   ),
            ("enable-universal-access-from-file-uris", True, '1.1.13'),
            ("enable-xss-auditor",                    False, '1.1.11'),
            ("tab-key-cycles-through-elements",       False, '1.1.17'),
        )

        settings = self.get_settings()
        for key, val, version in settings_values:
            try:
                settings.set_property(key, val)
            except TypeError:
                logging.warn(("Your version of WebKit does not support "
                    "the setting '{0}'.  This setting requires version "
                    "{1}.  For best compatibility, use at least version "
                    "1.1.22.").format(key, version))

    def load(self):
        if self.url is not None:
            self.open(self.url)
        else:
            self.load_string(*self.content)

    def call_js_function(self, name):
        self.execute_script(name + '()')

class BackwardsCompatibleFullscreenWindow(gtk.Window):
    def __init__(self, default_size):
        gtk.Window.__init__(self)

        self.screen = self.get_screen()

        self.listen_for_wm_changes()
        self.check_fullscreen_supported()

        self.set_default_size(*default_size)
        self.restore_to_size = default_size
        self.restore_to_position = self.get_position()
        self.is_fullscreen = False

    def listen_for_wm_changes(self):
        self.listen_for_wm_selection_changes()
        self.listen_for_root_property_changes()

    def listen_for_wm_selection_changes(self):
        # Clipboard is misleadingly named -- it's a selection!  the clipboard
        # is just one use for selections.  the WM_Sn selection must be owned by
        # the currently running window manager.  by monitoring changes in its
        # ownership, we can know when the current window manager has exited, or
        # when a new one has started.  this goes way back to the ICCCM spec and
        # should be compatible with even old or primitive WMs.
        self.screen_selection_atom_names = (
            'WM_S' + str(self.screen.get_number()),
            '_NET_WM_CM_S' + str(self.screen.get_number()), # CM = compositing manager
        )
        for atom_name in self.screen_selection_atom_names:
            selection = gtk.Clipboard(selection=atom_name)
            selection.connect('owner-change', self._wm_selection_owner_change_cb)

    def listen_for_root_property_changes(self):
        root_widget = gtk.Window()
        root_widget.realize()
        root_widget.connect('property-notify-event', self._root_property_change_cb)

        root = self.get_root_window()
        root.set_user_data(root_widget) # set_user_data is misleadingly named -- see the docs
        root.set_events(gtk.gdk.PROPERTY_CHANGE_MASK)

        self.commonly_changed_upon_wm_startup = (
            'WM_ICON_SIZE',
            '_NET_SUPPORTING_WM_CHECK',
            '_NET_SUPPORTED',
            '_NET_WORKAREA',
            '_NET_DESKTOP_NAMES',
            '_NET_DESKTOP_GEOMETRY',
            '_NET_NUMBER_OF_DESKTOPS',
        )

    def _root_property_change_cb(self, window, event):
        if event.atom in self.commonly_changed_upon_wm_startup:
            self.check_fullscreen_supported()
            self.restore_fullscreen_flag_after_wm_change()

    def _wm_selection_owner_change_cb(self, selection, event):
        if event.selection in self.screen_selection_atom_names:
            self.check_fullscreen_supported()
            self.restore_fullscreen_flag_after_wm_change()

    def restore_fullscreen_flag_after_wm_change(self):
        if self.fullscreen_supported:
            # we just possibly went through a period of time with no WM, and
            # now it's back. since the WM is in charge of updating the
            # _NET_WM_STATE property, that property is now potentially
            # inaccurate, with regard to fullscreen state.  let's get the newly
            # arrived WM to update it to its correct value, so that it doesn't
            # inadvertantly fullscreen us when we no longer want to be.
            if self.is_fullscreen:
                gtk.Window.fullscreen(self)
            else:
                gtk.Window.unfullscreen(self)

    def check_modern_window_manager_running(self):
        # the official explanation of this logic is at
        # http://standards.freedesktop.org/wm-spec/latest/ in the "root window
        # properties" section.

        # if a modern (EWMH-compliant) WM is running, then the root window
        # should have a property called _NET_SUPPORTING_WM_CHECK.
        supports_wm_check = gtk.gdk.get_default_root_window().property_get('_NET_SUPPORTING_WM_CHECK')

        self.wm_name = '<none>'

        if supports_wm_check:
            type, format, window_ids = supports_wm_check

            # the value of the _NET_SUPPORTING_WM_CHECK property should be a
            # list of window IDs whose length is 1.
            if window_ids:

                # the window ID in that list refers to an invisible dummy
                # window whose purpose is basically just to prove that the WM
                # is EWMH-compliant.
                window = gtk.gdk.window_foreign_new(window_ids[0])

                if not window:
                    # the documentation leads you to believe that if the dummy
                    # window is missing, then window_foreign_new should return
                    # None.  however, that doesn't seem to be accurate for me
                    # at all.  but just in case they fix that, i'll leave this
                    # if statement around...
                    return False

                # if the dummy window does appear to exist, then let's check if
                # we can read its _NET_WM_NAME property without getting an
                # error.  that will be the final indication of whether the WM
                # is running or not.

                gtk.gdk.error_trap_push()
                result = window.property_get('_NET_WM_NAME')
                if result:
                    self.wm_name = result[2]
                self.screen.get_display().sync()
                return not gtk.gdk.error_trap_pop()

        return False

    def check_fullscreen_supported(self):
        response = gtk.gdk.get_default_root_window().property_get('_NET_SUPPORTED')
        if not response:
            supported = []
        else:
            type, format, supported = response

        # why do we also need to check that an EWMH-compliant WM is running, instead
        # of just checking that _NET_SUPPORTED contains
        # _NET_WM_ACTION_FULLSCREEN?  because the _NET_SUPPORTED property could
        # be stale, left over from a window manager that is not running
        # anymore.

        self.fullscreen_supported = '_NET_WM_ACTION_FULLSCREEN' in supported \
                and self.check_modern_window_manager_running()

        logging.debug('WM just changed to {0}. is EWMH fullscreen supported? {1}'
            .format(self.wm_name, self.fullscreen_supported))

    def apply_legacy_fullscreen(self):
        self.set_decorated(False)
        self.move(0, 0)
        self.resize(self.screen.get_width(), self.screen.get_height())

    def undo_legacy_fullscreen(self):
        self.set_decorated(True)
        self.resize(*self.restore_to_size)
        self.move(*self.restore_to_position)

    def fullscreen(self):
        # this extra complexity is to handle situations where no window manager
        # is running.  in those cases, fullscreen() does nothing (although GTK
        # will still internally report WINDOW_STATE_FULLSCREEN if you ask).  so
        # we just manually set the window to the screen's size.

        self.restore_to_size = self.get_size()
        self.restore_to_position = self.get_position()

        self.is_fullscreen = True
        gtk.Window.fullscreen(self)
        if not self.fullscreen_supported:
            self.apply_legacy_fullscreen()

    def unfullscreen(self):
        self.is_fullscreen = False
        gtk.Window.unfullscreen(self)
        if not self.fullscreen_supported:
            self.undo_legacy_fullscreen()

class WebBrowser(BackwardsCompatibleFullscreenWindow):
    def __init__(self, url_handler_cb, **kw):
        BackwardsCompatibleFullscreenWindow.__init__(self, (800, 600))

        self.url_handler_cb = url_handler_cb

        self.connect('destroy', self._destroy_cb)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0x11*0xff, 0x11*0xff, 0x11*0xff))

        self.web_view = HTPickerWebView(**kw)
        self.web_view.connect('document-load-finished', self._ready_cb)
        self.web_view.connect('resource-request-starting', self._resource_cb)
        self.web_view.load()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scrolled_window.add(self.web_view)

        self.add(scrolled_window)

    def _resource_cb(self, view, frame, resource, request, response):
        self.url_handler_cb(request)

    def _ready_cb(self, *a, **k):
        self.show_all()

    def _destroy_cb(self, window):
        window.destroy()
        gtk.main_quit()

def URLAction(f):
    f._is_url_action = True
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

class URLHandler(object):
    """
    A URL Handler for a given network scheme.

    This assumes URIs of the form "scheme://method".  If you register with the
    scheme "foo", then the URI "foo://bar" will call your bar() method.

    Query string parameters will be translated into Python keyword arguments
    and passed to your method.  If you use a query parameter more than once,
    the multiple values will be rolled up into a list.  E.g:

        yourapp://yourmethod?a=one&a=two&b=three

    will become:

        yourmethod(a=['one', 'two'], b='three')

    You must decorate your action methods with the URLAction decorator.  It
    should look something like this:

        @URLAction
        def yourmethod(a, b):
            ...
    """

    def __init__(self, scheme):
        self.scheme = scheme

    def return_uri_filter(self, uri):
        """
        If all of your methods are going to do something similar with their
        results, such as formatting a data: URI, then you can consolidate that
        logic here.
        """
        return uri

    def handle_request(self, request):
        # i don't use urlparse.urlsplit() because it doesn't parse the
        # netloc/path of non-http:// URLs in the usual way.
        uri = request.get_uri()

        if not uri.startswith(self.scheme+'://'):
            return

        scheme, rest = uri.split('://', 1)

        if '?' in rest:
            action, qs = rest.split('?')
        else:
            action = rest
            qs = ''

        q = urlparse.parse_qs(qs)

        params = {}
        for key, values in q.items():
            params[key] = values[0] if len(values) == 1 else values

        method = getattr(self, action)
        if not hasattr(method, '_is_url_action'):
            raise RuntimeError("method {0} needs to be decorated with @URLAction.".format(action))
        ret = method(**params)

        new_uri = self.return_uri_filter(ret)

        if new_uri:
            request.set_uri(new_uri)
