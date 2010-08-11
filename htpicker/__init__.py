#!/usr/bin/env python

import glib
import gtk
import os
import pkg_resources

from htpicker.browser import WebBrowser
from htpicker.config import load_config
from htpicker.handler import MyHandler

# bug! alert() hangs the app... sometimes

def main():
    gtk.gdk.threads_init()

    config = load_config(os.path.expanduser("~/.htpickerrc"))

    handler = MyHandler('htpicker', config)

    html = pkg_resources.resource_string(__name__, 'data/app.html')

    webbrowser = WebBrowser(handler.handle_request, content=html,
            mime_type='text/html', encoding='utf-8', base_uri='file://')

    if config.getboolean_default('options', 'fullscreen', False):
        webbrowser.fullscreen()

    try:
        import pylirc
    except ImportError:
        print "pylirc is not installed. Install it if you wish to use a remote."
    else:
        from htpicker.lirc import LIRCEventSource, LIRCEventHandler
        lirc_source = LIRCEventSource('htpicker')
        lirc_handler = LIRCEventHandler(lirc_source, webbrowser.web_view)
        glib.io_add_watch(lirc_source.fileno, glib.IO_IN, lirc_handler)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
