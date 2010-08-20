#!/usr/bin/env python

import glib
import gtk
import os
import pkg_resources
import sys

from htpicker.browser import WebBrowser
from htpicker.config import HTPickerConfig
from htpicker.handler import MyHandler
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
            print "pyinotify is not installed. Install it if you want automatic"
            print "re-scaning of directories when files change."
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
            print "pylirc is not installed. Install it if you wish to use a remote."
        else:
            from htpicker.lirc import LIRCEventSource, LIRCEventHandler
            lirc_source = LIRCEventSource('htpicker')
            lirc_handler = LIRCEventHandler(lirc_source, webbrowser, webbrowser.web_view)
            glib.io_add_watch(lirc_source.fileno, glib.IO_IN, lirc_handler)

    def init_joysticks(self, webbrowser):
        joysticks = Joystick.create_all()
        for joystick in joysticks:
            joystick_handler = JoystickEventHandler(joystick, webbrowser, webbrowser.web_view, 250, 100)
            glib.io_add_watch(joystick.device_file, glib.IO_IN, joystick_handler)

    def run(self):
        gtk.gdk.threads_init()

        self.config = HTPickerConfig(os.path.expanduser("~/.htpickerrc"), sys.argv)

        handler = MyHandler('htpicker', self.config, self.dir_change_cb)

        html = pkg_resources.resource_string(__name__, 'data/app.html')

        webbrowser = WebBrowser(handler.handle_request, content=html,
                mime_type='text/html', encoding='utf-8', base_uri='file://')

        if self.config.getboolean_default('options', 'fullscreen', False):
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
