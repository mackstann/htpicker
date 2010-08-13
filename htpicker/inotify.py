#!/usr/bin/env python

import pyinotify

class GlibNotifier(pyinotify.Notifier):
    def __init__(self, handler):
        self.wm = pyinotify.WatchManager()
        super(GlibNotifier, self).__init__(self.wm, handler)
        self.mywd = self.wm.add_watch('/tmp', pyinotify.IN_DELETE | pyinotify.IN_CREATE)

    def get_fd(self):
        return self.wm.get_fd()

    def __call__(self, fd, io_condition):
        self.read_events()
        self.process_events()
        return True # stay attached to the main loop

class INotifyHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "created:", event.pathname

    def process_IN_DELETE(self, event):
        print "deleted:", event.pathname

    def change_dir(self, directory):
        print 'new dir:', directory

