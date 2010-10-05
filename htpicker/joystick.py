#!/usr/bin/env python

import glib
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

    HORIZONTAL_AXIS = 0 # even numbered axes are horizontal,
    VERTICAL_AXIS = 1   # odd are vertical.  generally.
    MAX_AXIS_VALUE = 32767

    def __init__(self, bytestring, axis_threshold, digitize):
        self.time, self.value, self.rawtype, self.number = struct.unpack(self.struct_format, bytestring)
        self.is_initial = bool(self.rawtype & self.INIT)
        self.rawtype &= ~self.INIT

        if self.rawtype == JoystickEvent.AXIS:
            if abs(self.value) / float(self.MAX_AXIS_VALUE) < axis_threshold:
                self.value = 0
            if digitize and self.value:
                self.value = self.digitize(self.value)

        if self.rawtype == self.BUTTON:
            self.type = [self.BUTTON_RELEASE, self.BUTTON_PRESS][self.value]
        else:
            self.type = self.rawtype

    @staticmethod
    def digitize(axis_value):
        """simplify any number down to -1, 0, or 1"""
        if axis_value == 0:
            return 0
        return axis_value / abs(axis_value)

class JoystickEventHandler(object):
    def __init__(self, source, window, web_view, repeat_delay, repeat_interval):
        self.source = source
        self.window = window
        self.web_view = web_view
        self.repeat_delay = repeat_delay
        self.repeat_interval = repeat_interval
        self.event_id = None
        self.last_axis_event = None

    def __call__(self, fd, io_condition):
        self.handle_event()
        return True # stay attached to the main loop

    def handle_event(self):
        e = self.source.get_event()

        # enforce window focus.
        if not self.window.has_toplevel_focus():
            return

        if e.type == JoystickEvent.BUTTON_PRESS and not e.is_initial:
            self.disable_repeat()
            if e.number == 1:
                self.fire('go_parent_directory')
            else:
                self.fire('activate_current_selection')

        elif e.type == JoystickEvent.AXIS:
            axis_event = (e.number, JoystickEvent.digitize(e.value))
            if axis_event != self.last_axis_event:
                self.last_axis_event = axis_event
                self.disable_repeat()

            if e.number == JoystickEvent.VERTICAL_AXIS:
                if e.value < 0:
                    self.start_repeat('move_selection_up')
                elif e.value > 0:
                    self.start_repeat('move_selection_down')
            elif e.number == JoystickEvent.HORIZONTAL_AXIS:
                if e.value < 0:
                    self.fire('hide_menu')
                elif e.value > 0:
                    self.fire('show_menu')

    def fire(self, function=None):
        self.web_view.call_js_function(function if function else self.repeated_function)

    def start_repeat(self, repeated_function):
        self.disable_repeat()
        self.repeated_function = repeated_function
        self.fire()
        self.event_id = glib.timeout_add(self.repeat_delay, self.continue_repeat)

    def continue_repeat(self):
        self.fire()
        self.event_id = glib.timeout_add(self.repeat_interval, self.continue_repeat)
        return False

    def disable_repeat(self):
        if self.event_id is not None:
            glib.source_remove(self.event_id)
            self.event_id = None
