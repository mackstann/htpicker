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

import gobject
import gtk
import webkit

gtk.gdk.threads_init()

class ContentPane (gtk.VBox):
    __gsignals__ = {
        "new-window-requested": (gobject.SIGNAL_RUN_FIRST,
                                 gobject.TYPE_NONE,
                                 (gobject.TYPE_OBJECT,))
        }

    def __init__ (self):
        """initialize the content pane"""
        gtk.VBox.__init__(self)
        self.show_all()
        self.connect("new-window-requested", lambda *a, **k: None)

    def new_tab (self, url=None):
        """creates a new page in a new tab"""
        # create the tab content
        browser = webkit.WebView()
        browser.set_full_content_zoom(True)
        self._construct_tab_view(browser, url)

    def _construct_tab_view (self, web_view, url):
        web_view.open(url)

        web_view.connect("create-web-view", self._new_web_view_request_cb)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        self.add(scrolled_window)
        self.show_all()

    def _new_web_view_request_cb (self, web_view, web_frame):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        view = webkit.WebView()
        view.set_full_content_zoom(True)
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


class WebBrowser(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        content_tabs = ContentPane()

        self.add(content_tabs)
        self.set_default_size(800, 600)
        self.connect('destroy', destroy_cb, content_tabs)

        self.show_all()

        content_tabs.new_tab("http://www.google.com")

def destroy_cb(window, content_pane):
    """destroy window resources"""
    window.destroy()
    gtk.main_quit()

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
