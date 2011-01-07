#!/usr/bin/env python

import glib
import gtk
import logging
import os
import pkg_resources
import sys

from htpicker.browser import WebBrowser
from htpicker.config import HTPickerConfig
from htpicker.handler import HTPickerURLHandler
from htpicker.joystick import Joystick, JoystickEventHandler

# bug! alert() hangs the app... sometimes

class HTPicker(object):
    def dir_change_cb(self, directory):
        if self.inotifier is not None:
            self.inotifier.change_dir(directory)

    def init_inotify(self, webbrowser):
        try:
            import pyinotify
        except ImportError:
            logging.info("pyinotify is not installed. Install it if you want automatic re-scaning of directories when files change.")
            self.inotifier = None
        else:
            from htpicker.inotify import GlibNotifier, INotifyHandler
            ihandler = INotifyHandler(webbrowser.web_view)
            self.inotifier = GlibNotifier(ihandler)
            glib.io_add_watch(self.inotifier.get_fd(), glib.IO_IN, self.inotifier)

    def init_lirc(self, webbrowser):
        try:
            import pylirc
        except ImportError:
            logging.info("pylirc is not installed. Install it if you wish to use a remote.")
        else:
            from htpicker.lirc import LIRCEventSource, LIRCEventHandler
            try:
                lirc_source = LIRCEventSource('htpicker')
            except RuntimeError, e:
                logging.warn("pylirc failed to initialize, with the following error: " + str(e))
                logging.warn("... this may be because your LIRC isn't configured, or no IR receiver is connected.")
            else:
                lirc_handler = LIRCEventHandler(lirc_source, webbrowser, webbrowser.web_view)
                glib.io_add_watch(lirc_source.fileno, glib.IO_IN, lirc_handler)

    def init_joysticks(self, webbrowser):
        joysticks = Joystick.create_all()
        for joystick in joysticks:
            joystick_handler = JoystickEventHandler(joystick, webbrowser, webbrowser.web_view, 250, 100)
            glib.io_add_watch(joystick.device_file, glib.IO_IN, joystick_handler)

    def run(self):
        gtk.gdk.threads_init()

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        self.config = HTPickerConfig(os.path.expanduser("~/.htpickerrc"), sys.argv)

        handler = HTPickerURLHandler('htpicker', self.config, self.dir_change_cb)

        html = pkg_resources.resource_string(__name__, 'data/app.html')

        webbrowser = WebBrowser(handler.handle_request,
                content=(html, 'text/html', 'utf-8', 'file://'))

        handler.browser = webbrowser # ugly workaround for mutual dependency

        if self.config.get_fullscreen():
            webbrowser.fullscreen()

        self.init_inotify(webbrowser)
        self.init_lirc(webbrowser)
        self.init_joysticks(webbrowser)

        try:
            gtk.main()
        except KeyboardInterrupt:
            pass

        return 0

def main():
    return HTPicker().run()

if __name__ == "__main__":
    raise SystemExit(main())
