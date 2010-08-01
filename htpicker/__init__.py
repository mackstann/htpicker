#!/usr/bin/env python

import gtk
import pkg_resources

from htpicker.browser import WebBrowser
from htpicker.config import load_config
from htpicker.handler import MyHandler

# bug! alert() hangs the app... sometimes

def main():
    gtk.gdk.threads_init()

    config = load_config()

    handler = MyHandler('htpicker', config)

    html = pkg_resources.resource_string(__name__, 'data/app.html')

    webbrowser = WebBrowser(handler.handle_request, content=html,
            mime_type='text/html', encoding='utf-8', base_uri='file://')

    if config.getboolean_default('options', 'fullscreen', False):
        webbrowser.fullscreen()

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
