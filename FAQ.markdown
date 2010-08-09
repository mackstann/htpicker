Frequently Asked Questions
==========================

How can I add a simple program launcher that doesn't play any particular file?
------------------------------------------------------------------------------

Just place the executable (or probably better, a symlink to one) where you want
it to appear in your directory structure, name it whatever you like, and then
add a section to your .htpickerrc that simply has "{file}" as the command.  For
example:

    [programs]
    command = {file}
    matches = ~/programs/*

Now, if I make a symlink for Banshee like this:

    $ ln -s /usr/bin/banshee ~/programs/Banshee
    $ ls -l ~/programs
    lrwxrwxrwx 1 nick nick 16 2010-08-08 20:56 Banshee -> /usr/bin/banshee*

Then I will now have an item "Banshee" inside of ~/programs that will launch
/usr/bin/banshee.

You can also be more selective, instead of globbing an entire directory:

    [programs]
    command = {file}
    matches = ~/Videos/HandBrake, ~/Videos/dvd::rip, ~/Music/Sound Juicer
