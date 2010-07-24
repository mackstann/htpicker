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

class WebBrowser(gtk.Window):

    def __init__(self, url, url_handler):
        gtk.Window.__init__(self)

        self.url_handler = url_handler

        web_view = webkit.WebView()
        web_view.set_full_content_zoom(True)

        settings = web_view.get_settings()
        #settings.set_property("enable-default-context-menu", False)
        #settings.set_property("enable-java-applet", False)
        #settings.set_property("enable-plugins", False)
        settings.set_property("enable-universal-access-from-file-uris", True)
        settings.set_property("enable-xss-auditor", False)
        #settings.set_property("tab-key-cycles-through-elements", False)

        #web_view.open(url)
        web_view.load_string('<html><body>hi<img src="myapp://foo"></body></html>', "text/html", "iso-8859-15", 'file:///foo/')

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        self.add(scrolled_window)

        self.set_default_size(800, 600)
        self.connect('destroy', self._destroy_cb)
        web_view.connect('resource-request-starting', self._resource_cb)

        self.show_all()

    def _destroy_cb(self, window):
        window.destroy()
        gtk.main_quit()

    def _resource_cb(self, view, frame, resource, request, response):
        self.url_handler.handle_request(resource.get_uri())

class URLHandler(object):
    def __init__(self, scheme):
        self.scheme = scheme

    def handle_request(self, uri):
        if uri.startswith(self.scheme + '://'):
            action = uri.split('://', 1)[1]
            getattr(self, action)()

if __name__ == "__main__":
    class MyHandler(URLHandler):
        def foo(self):
            print 'callback from a url request!'
    handler = MyHandler('myapp')
    webbrowser = WebBrowser('http://google.com', handler)
    gtk.main()
