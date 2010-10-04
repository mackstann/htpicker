About
=====

htpicker is a simple home theater frontend program that lets you browse
directories and launch arbitrary files with programs of your choosing.

Dependencies
============

You will need Python, the WebKit library (libwebkit) as well as the Python GTK
bindings for it (pywebkitgtk; the Ubuntu package is python-webkit).

Downloading
===========

There are no releases yet, so you will need git installed, and do a git clone:

    $ git clone git@github.com:mackstann/htpicker.git

Installation
============

    $ cd htpicker
    $ python setup.py build
    $ sudo python setup.py install

Usage
=====

    $ htpicker [directory]

[directory] is optional and defaults to the current directory.

After its first run, you will now have a ~/.htpickerrc config file that you can
edit to add support for more file types and programs to play them, as well as
file patterns to ignore, and toggling fullscreen mode.

General Controls
================

You can control htpicker by any combination of keyboard, joystick, or remote
control.  It only cares about 6 buttons: left, right, up, down, "select", and
"back".  Up and down scroll through menu choices.  Right displays the options
menu.  Left closes it.  "Select" and "back" should be self-explanatory.

Keyboard Controls
=================

The enter key acts as "select".  There is no keyboard mapping for a "back"
button, but it will be coming soon.  You can get around this by scrolling to
the top and selecting the parent directory.

Joystick Controls
=================

Any standard USB HID joystick recognized by Linux should work.  The button
numbered #1 by the hardware will act as a "back" button, and every other button
will act as a select/OK button.  The jstest program (not a part of htpicker)
may be helpful in figuring out the button configuration of your joystick.  If
multiple joysticks are present, htpicker will listen to all of them.

Remote Control
==============

htpicker can be controlled by a remote control via LIRC.  Get LIRC installed
and configured for your remote, then see the example config file in htpicker's
extras directory.  There's one config file for htpicker itself, and another
that you may find useful for controlling mplayer.

Motivation and Design
=====================

I created htpicker because I was unsatisfied with all other HTPC frontend
software I've tried.  They're all complicated monstrosities and I seem to
have a talent for finding their bugs.  All I really wanted was a way to browse
a directory structure in a TV-friendly visual format, and launch files with
external programs (e.g. a video with mplayer, or a video game ROM with an
emulator).

There are no over-complicated plugins, scripts, XML files, or anything like
that.  There is one small configuration file located at ~/.htpickerrc.  This
file will be created for you the first time you run htpicker.  The meat of this
config file is mapping certain directories and/or file extensions to programs
that can play them.  The stock config file sets up a few reasonable defaults,
such as using mplayer to play files in ~/Videos as well as files with common
video filename extensions, and playing a couple types of video game ROMs with
their respective console emulators.  You can change or expand these settings to
play any file with any program you want.

And why not just use HTML and Javascript for the UI?  So that's what I've done.
The program you run consists of three parts:  The first is a generic browser
window, using WebKit, the same HTML engine used by Chrome, Safari, and the
iPhone and Android browsers.  The second part is the HTML and Javascript web
page that this browser displays.  The third is a backend program that gets
requests from the webpage and executes actions that are impossible from within
a webpage, such as reading the contents of a directory on the filesystem, or
executing a program to play a file.

Since htpicker's GUI is written in HTML and JavaScript (using WebKit), it does
not engage any special video modes or cause problems with switching to other
programs. It can run in a window or fullscreen (the toggle is in the config
file). Despite using WebKit for its GUI, it is not a web application, and does
not access the network in any way.
