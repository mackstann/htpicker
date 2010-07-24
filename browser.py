#!/usr/bin/env python
# Copyright (C) 2007, 2008, 2009 Jan Michael Alonzo <jmalonzo@gmai.com>
# Copyright (C) 2010 Nick Welch <nick@incise.org>
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

import gtk
import webkit

gtk.gdk.threads_init()

class ContentPane (gtk.VBox):
    def __init__ (self):
        """initialize the content pane"""
        gtk.VBox.__init__(self)
        self.show_all()

    def new_tab (self, url=None):
        """creates a new page in a new tab"""
        # create the tab content

class WebBrowser(gtk.Window):
    def __init__(self, url):
        gtk.Window.__init__(self)

        web_view = webkit.WebView()
        web_view.set_full_content_zoom(True)
        web_view.open(url)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        self.add(scrolled_window)

        self.set_default_size(800, 600)
        self.connect('destroy', destroy_cb)

        self.show_all()

def destroy_cb(window):
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
    webbrowser = WebBrowser('http://google.com')
    gtk.main()
