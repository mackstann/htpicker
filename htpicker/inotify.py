#!/usr/bin/env python

import pyinotify
import time

class GlibNotifier(pyinotify.Notifier):
    def __init__(self, handler):
        self.wm = pyinotify.WatchManager()
        super(GlibNotifier, self).__init__(self.wm, handler)
        self.wd = None
        self.directory = None

    def get_fd(self):
        return self.wm._fd

    def change_dir(self, directory):
        self.remove_watch()
        self.directory = directory
        self.add_watch()

    def close(self):
        if self.wd is not None:
            self.wm.rm_watch(self.wd)
            self.wd = None

    def open(self):
        if self.directory is not None:
            wd_dict = self.wm.add_watch(self.directory, pyinotify.IN_DELETE | pyinotify.IN_CREATE)
            self.wd = wd_dict.values()[0] # we will only ever have one to deal with at a time.

    def __call__(self, fd, io_condition):
        self.read_events()
        self.process_events()
        return True # stay attached to the main loop

class INotifyHandler(pyinotify.ProcessEvent):
    throttle_interval = 0.6

    def __init__(self, web_view):
        self.web_view = web_view
        self.last_refresh = 0

    def throttled_refresh(self):
        now = time.time()
        if now - self.last_refresh > self.throttle_interval:
            self.web_view.call_js_function('load_files')
            self.last_refresh = now

    def process_IN_CREATE(self, event):
        self.throttled_refresh()

    def process_IN_DELETE(self, event):
        self.throttled_refresh()
