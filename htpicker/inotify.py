#!/usr/bin/env python

import os
import pyinotify

class GlibNotifier(pyinotify.Notifier):
    def __init__(self, handler):
        self.wm = pyinotify.WatchManager()
        super(GlibNotifier, self).__init__(self.wm, handler)
        self.wd = None

    def get_fd(self):
        return self.wm.get_fd()

    def change_dir(self, directory):
        print 'new dir:', directory
        if self.wd is not None:
            print self.wd
            self.wm.rm_watch(self.wd)
        wd_dict = self.wm.add_watch(directory, pyinotify.IN_DELETE | pyinotify.IN_CREATE)
        self.wd = wd_dict.values()[0] # we will only ever have one to deal with at a time.

    def __call__(self, fd, io_condition):
        self.read_events()
        self.process_events()
        return True # stay attached to the main loop

class INotifyHandler(pyinotify.ProcessEvent):
    def __init__(self, web_view):
        self.web_view = web_view

    def process_IN_CREATE(self, event):
        print "created:", event.pathname
        self.web_view.call_js_function('load_files')

    def process_IN_DELETE(self, event):
        print "deleted:", event.pathname
        self.web_view.call_js_function('load_files')

