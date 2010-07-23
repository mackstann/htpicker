#!/usr/bin/env python
# Copyright (C) 2007, 2008, 2009 Jan Michael Alonzo <jmalonzo@gmai.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# TODO:
#
# * fix tab relabelling
# * search page interface
# * custom button - w/o margins/padding to make tabs thin
#

from gettext import gettext as _

import gobject
import gtk
import pango
import webkit

gtk.gdk.threads_init()

class BrowserPage(webkit.WebView):

    def __init__(self):
        webkit.WebView.__init__(self)
        settings = self.get_settings()

        # scale other content besides from text as well
        self.set_full_content_zoom(True)

class TabLabel (gtk.HBox):
    """A class for Tab labels"""

    __gsignals__ = {
        "close": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  (gobject.TYPE_OBJECT,))
        }

    def __init__ (self, title, child):
        """initialize the tab label"""
        gtk.HBox.__init__(self, False, 4)
        self.title = title
        self.child = child
        self.label = gtk.Label(title)
        self.label.props.max_width_chars = 30
        self.label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self.label.set_alignment(0.0, 0.5)

        icon = gtk.image_new_from_stock(gtk.STOCK_ORIENTATION_PORTRAIT, gtk.ICON_SIZE_BUTTON)
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button = gtk.Button()
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect("clicked", self._close_tab, child)
        close_button.set_image(close_image)
        self.pack_start(icon, False, False, 0)
        self.pack_start(self.label, True, True, 0)
        self.pack_start(close_button, False, False, 0)

        self.set_data("label", self.label)
        self.set_data("close-button", close_button)

    def set_label (self, text):
        """sets the text of this label"""
        self.label.set_label(text)

    def _close_tab (self, widget, child):
        self.emit("close", child)

class ContentPane (gtk.Notebook):

    __gsignals__ = {
        "focus-view-title-changed": (gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_OBJECT, gobject.TYPE_STRING,)),
        "new-window-requested": (gobject.SIGNAL_RUN_FIRST,
                                 gobject.TYPE_NONE,
                                 (gobject.TYPE_OBJECT,))
        }

    def __init__ (self):
        """initialize the content pane"""
        gtk.Notebook.__init__(self)
        self.props.scrollable = True
        self.props.homogeneous = True

        self.show_all()

    def load (self, text):
        """load the given uri in the current web view"""
        child = self.get_nth_page(self.get_current_page())
        view = child.get_child()
        view.open(text)

    def new_tab_with_webview (self, webview):
        """creates a new tab with the given webview as its child"""
        self._construct_tab_view(webview)

    def new_tab (self, url=None):
        """creates a new page in a new tab"""
        # create the tab content
        browser = BrowserPage()
        self._construct_tab_view(browser, url)

    def _construct_tab_view (self, web_view, url=None):
        web_view.connect("create-web-view", self._new_web_view_request_cb)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        # create the tab
        label = TabLabel(url, scrolled_window)
        label.connect("close", self._close_tab)
        label.show_all()

        new_tab_number = self.append_page(scrolled_window, label)
        self.set_tab_label_packing(scrolled_window, False, False, gtk.PACK_START)
        self.set_tab_label(scrolled_window, label)

        # hide the tab if there's only one
        self.set_show_tabs(self.get_n_pages() > 1)

        self.show_all()
        self.set_current_page(new_tab_number)

        # load the content
        if not url:
            web_view.load_string("hey", "text/html", "iso-8859-15", "about")
        else:
            web_view.open(url)

    def _close_tab (self, label, child):
        page_num = self.page_num(child)
        if page_num != -1:
            view = child.get_child()
            view.destroy()
            self.remove_page(page_num)
        self.set_show_tabs(self.get_n_pages() > 1)

    def _new_web_view_request_cb (self, web_view, web_frame):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        view = BrowserPage()
        scrolled_window.add(view)
        scrolled_window.show_all()

        vbox = gtk.VBox(spacing=1)
        vbox.pack_start(scrolled_window, True, True)

        window = gtk.Window()
        window.add(vbox)
        view.connect("web-view-ready", self._new_web_view_ready_cb)
        return view

    def _new_web_view_ready_cb (self, web_view):
        self.emit("new-window-requested", web_view)


class WebToolbar(gtk.Toolbar):

    __gsignals__ = {
        "load-requested": (gobject.SIGNAL_RUN_FIRST,
                           gobject.TYPE_NONE,
                           (gobject.TYPE_STRING,)),
        "new-tab-requested": (gobject.SIGNAL_RUN_FIRST,
                              gobject.TYPE_NONE, ()),
        "view-source-mode-requested": (gobject.SIGNAL_RUN_FIRST,
                                       gobject.TYPE_NONE,
                                       (gobject.TYPE_BOOLEAN, ))
        }

    def __init__(self):
        gtk.Toolbar.__init__(self)

    def _entry_activate_cb(self, entry):
        self.emit("load-requested", entry.props.text)

    def _add_tab_cb(self, button):
        self.emit("new-tab-requested")

    def _view_source_mode_cb(self, button):
        self.emit("view-source-mode-requested", button.get_active())

class WebBrowser(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        toolbar = WebToolbar()
        content_tabs = ContentPane()
        content_tabs.connect("new-window-requested", self._new_window_requested_cb)
        toolbar.connect("load-requested", load_requested_cb, content_tabs)
        toolbar.connect("new-tab-requested", new_tab_requested_cb, content_tabs)

        vbox = gtk.VBox(spacing=1)
        vbox.pack_start(toolbar, expand=False, fill=False)
        vbox.pack_start(content_tabs)

        self.add(vbox)
        self.set_default_size(800, 600)
        self.connect('destroy', destroy_cb, content_tabs)

        self.show_all()

        content_tabs.new_tab("http://www.google.com")

    def _new_window_requested_cb (self, content_pane, view):
        features = view.get_window_features()
        window = view.get_toplevel()

        scrolled_window = view.get_parent()
        if features.get_property("scrollbar-visible"):
            scrolled_window.props.hscrollbar_policy = gtk.POLICY_NEVER
            scrolled_window.props.vscrollbar_policy = gtk.POLICY_NEVER

        isLocationbarVisible = features.get_property("locationbar-visible")
        isToolbarVisible = features.get_property("toolbar-visible")
        if isLocationbarVisible or isToolbarVisible:
            toolbar = WebToolbar(isLocationbarVisible, isToolbarVisible)
            scrolled_window.get_parent().pack_start(toolbar, False, False, 0)

        window.set_default_size(features.props.width, features.props.height)
        window.move(features.props.x, features.props.y)

        window.show_all()
        return True

# event handlers
def new_tab_requested_cb (toolbar, content_pane):
    content_pane.new_tab("about:blank")

def load_requested_cb (widget, text, content_pane):
    if not text:
        return
    content_pane.load(text)

def destroy_cb(window, content_pane):
    """destroy window resources"""
    num_pages = content_pane.get_n_pages()
    while num_pages != -1:
        child = content_pane.get_nth_page(num_pages)
        if child:
            view = child.get_child()
        num_pages = num_pages - 1
    window.destroy()
    gtk.main_quit()

# context menu item callbacks
def about_pywebkitgtk_cb(menu_item, web_view):
    web_view.open("http://live.gnome.org/PyWebKitGtk")

#def zoom_in_cb(menu_item, web_view):
#    """Zoom into the page"""
#    web_view.zoom_in()
#
#def zoom_out_cb(menu_item, web_view):
#    """Zoom out of the page"""
#    web_view.zoom_out()
#
#def zoom_hundred_cb(menu_item, web_view):
#    """Zoom 100%"""
#    if not (web_view.get_zoom_level() == 1.0):
#        web_view.set_zoom_level(1.0)

if __name__ == "__main__":
    webbrowser = WebBrowser()
    gtk.main()
