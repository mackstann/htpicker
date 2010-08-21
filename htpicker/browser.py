#!/usr/bin/env python

import functools
import gtk
import logging
import time
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

class WebBrowser(gtk.Window):
    def __init__(self, url_handler_cb, **kw):
        gtk.Window.__init__(self)
        self.url_handler_cb = url_handler_cb

        self.connect('destroy', self._destroy_cb)
        self.set_default_size(800, 600)

        self.web_view = HTPickerWebView(**kw)
        self.web_view.connect('document-load-finished', self._ready_cb)
        self.web_view.connect('resource-request-starting', self._resource_cb)
        self.web_view.load()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

        scrolled_window.add(self.web_view)
        scrolled_window.show_all()

        self.add(scrolled_window)

        self.iconify()
        self.show_all()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0x11*0xff, 0x11*0xff, 0x11*0xff))

    def _resource_cb(self, view, frame, resource, request, response):
        self.url_handler_cb(request)

    def _ready_cb(self, *a, **k):
        time.sleep(0.2)
        self.deiconify()

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
