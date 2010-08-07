About
=====

HTPicker is a simple home theater frontend program that lets you browse
directories and launch arbitrary files with programs of your choosing.

Installation
============

$ python setup.py build
$ sudo python setup.py install

Usage
=====

$ htpicker [directory]

[directory] is optional and defaults to the current directory.

The arrow keys move the selection up and down, and the enter key will open the
selected file/folder.

Motivation and Design
=====================

I created HTPicker because I was unsatisfied with all other HTPC frontend
software I've tried.  They're all complicated monstrosities and I seem to
attract their bugs.

All I really wanted was a way to browse a directory structure in a TV-friendly
visual format, and launch files with external programs (e.g. a video with
mplayer, or a video game ROM with an emulator).

And why not just use HTML and Javascript for the UI?  So that's what I've done.
The program you run consists of three parts:  The first is a generic browser
window, using WebKit, the same HTML engine used by Chrome, Safari, and the
iPhone and Android browsers.  The second part is the HTML and Javascript web
page that this browser displays.  The third is a backend program that gets
requests from the webpage and executes actions that are impossible from within
a webpage, such as reading the contents of a directory on the filesystem, or
executing a program to play a file.

HTPicker also doesn't care about your screen resolution or anything else
related to your video setup, any more than Firefox or Chrome or MPlayer would.

To do
=====

* There is currently no convenient way to exit the program, which is especially
  annoying since it runs full screen, so you don't have a window titlebar or
  close button.  Ctrl-C it if you run it from a shell, or kill it via whatever
  means are at your disposal.

* Remote (lirc) support, or at least documentation of how to do it.

* Joystick support
