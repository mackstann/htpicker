#!/usr/bin/env python

import glob
import struct

class Joystick(object):
    def __init__(self, filename, axis_threshold=0.1, digitize=True):
        self.device_file = open(filename)
        self.axis_threshold = axis_threshold
        self.digitize = digitize

    @classmethod
    def create_all(cls):
        return [ cls(fn) for fn in glob.glob('/dev/input/js[0-9]*') ]

    def get_event(self):
        bytestring = self.device_file.read(JoystickEvent.struct_size)
        return JoystickEvent(bytestring, self.axis_threshold, self.digitize)

class JoystickEvent(object):
    struct_format = "IhBB"
    struct_size = struct.calcsize(struct_format)

    BUTTON = 0x01
    AXIS = 0x02
    INIT = 0x80

    BUTTON_RELEASE = 0
    BUTTON_PRESS = 1

    MAX_AXIS_VALUE = 32767

    def __init__(self, bytestring, axis_threshold, digitize):
        self.time, self.value, self.rawtype, self.number = struct.unpack(self.struct_format, bytestring)
        self.rawtype &= ~self.INIT

        if self.rawtype == JoystickEvent.AXIS:
            if abs(self.value) / float(self.MAX_AXIS_VALUE) < axis_threshold:
                self.value = 0
            if digitize and self.value:
                self.value /= abs(self.value) # now it is one of [-1, 0, 1]

        if self.rawtype == self.BUTTON:
            self.type = [self.BUTTON_RELEASE, self.BUTTON_PRESS][self.value]
        else:
            self.type = self.rawtype

class JoystickEventHandler(object):
    def __init__(self, source, window, web_view):
        self.source = source
        self.window = window
        self.web_view = web_view

    def __call__(self, fd, io_condition):
        self.handle_event()
        return True # stay attached to the main loop

    def handle_event(self):
        e = self.source.get_event()

        # enforce window focus.
        if not self.window.has_toplevel_focus():
            return

        if e.type == JoystickEvent.BUTTON_PRESS:
            if e.number == 1:
                self.web_view.call_js_function('go_parent_directory')
            else:
                self.web_view.call_js_function('activate_current_selection')
        elif e.type == JoystickEvent.AXIS and e.number % 2 == 1:
            if e.value < 0:
                self.web_view.call_js_function('move_selection_up')
            elif e.value > 0:
                self.web_view.call_js_function('move_selection_down')
