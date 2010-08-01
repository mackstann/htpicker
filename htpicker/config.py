#!/usr/bin/env python

import ConfigParser
import os

class MyConfigParser(ConfigParser.RawConfigParser):
    def get_default(self, section, option, default, **kwargs):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option).format(**kwargs)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return default

    def getboolean_default(self, section, option, default):
        try:
            return ConfigParser.RawConfigParser.getboolean(self, section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return default

    def getlist_default(self, section, option, default, **kwargs):
        val = self.get_default(section, option, default, **kwargs)

        # the default is passed as a list type, so don't text-manipulate it.
        if val == default:
            return default

        return map(str.strip, val.split(','))

def load_config():
    filename = os.path.expanduser("~/.htpickerrc")

    if not os.path.isfile(filename):
        f = open(filename, 'w')
        f.write(default_config)
        f.close()
        print "I have created a ~/.htpickerrc config file for you."
        print "Take a look and edit it to your liking."

    config = MyConfigParser()
    config.read(filename)
    return config

default_config = """
# How this config file works:
#
# Each section describes an external program used to play certain files, and
# then lists which files should be played by that program.  Each section has up
# to five lines.  Here is an example, followed by an explanation of each line.
#
# (Line 1) [mplayer]
# (Line 2) command = mplayer -fs {file}
# (Line 3) folders = ~/Videos, ~/Video
# (Line 4) matches = *.avi, *.mkv, *.mpg, *.mp4, *.flv
# (Line 5) icon = video
#
# Line 1 contains the section name.  This is solely for your own reference.
#
# Line 2 contains a command to play files with.  The special term "{file}"
# indicates where the filename should go when executing the command.  Do not
# put quotes around it -- the proper quoting and escaping will be done
# automatically.
#
# Line 3 lists folders (comma-delimited) whose files this command should always
# be used to play.
#
# Line 4 lists file types (filename glob patterns, comma-delimited) that this
# command can play.  These are a fallback, and are only obeyed in folders which
# have not been specifically assigned somewhere in a "folders" line (line 3).
#
# Line 5 states which icon to show for these files.  Options are 'video' and
# 'game'.
#
# For gritty details on what special characters may go into filename match
# patterns, run the command 'pydoc fnmatch.fnmatch'.
#
# A few reasonable defaults have been put here for you:

[mplayer]
# this -geometry option is highly recommended, otherwise you will often get a
# briefly visible "phantom" mplayer window, before mplayer goes full screen.
command = mplayer -geometry 1x1+4000+4000 -fs {file}
folders = ~/Videos, ~/Video
matches = *.avi, *.mkv, *.mpg, *.mp4, *.flv
icon = video

[zsnes]
command = zsnes {file}
folders = ~/ROMs/SNES
matches = *.smc, *.fig, *.zip
icon = game

[fceu]
command = fceu -fs 1 {file}
folders = ~/ROMs/NES
matches = *.nes *.nes.gz
icon = game

# And here is the global options section.
[options]

# File patterns to ignore.
ignore = .*, *~, *.bak, *.nfo, *.txt, *.url, *.sfv, *.part*.rar
fullscreen = off
"""
