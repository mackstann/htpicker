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

def write_default_config(filename):
    f = open(filename, 'w')
    f.write(default_config)
    f.close()

def back_compat_check_folders_setting(config):
    warn = False
    for section in config.sections():
        if config.getlist_default(section, 'folders', None) != None:
            write_default_config('/tmp/htpickerrc-new-default')
            print "Warning: The 'folders' setting is no longer supported."
            print "         It has been consolidated with the 'matches'"
            print "         setting.  Simply take the folders in the"
            print "         'folders' setting, add a '/*' to them, and put"
            print "         them into the 'matches' setting.  E.g. '~/Videos'"
            print "         would become '~/Videos/*'.  I have written the new"
            print "         default config file to /tmp/htpickerrc-new-default"
            print "         in case you want to examine it for further"
            print "         clarification."
            return

def load_config(filename):
    if not os.path.isfile(filename):
        write_default_config(filename)
        print "I have created a ~/.htpickerrc config file for you."
        print "Take a look and edit it to your liking."

    config = MyConfigParser()
    config.read(filename)
    back_compat_check_folders_setting(config)
    return config

default_config = """
# How this config file works:
#
# Each section describes an external program used to play certain files, and
# then lists which files should be played by that program.  Each section has up
# to four lines.  Here is an example, followed by an explanation of each line.
#
# (Line 1) [mplayer]
# (Line 2) command = mplayer -fs {file}
# (Line 3) matches = ~/Videos/*, ~/Video/*, *.avi, *.mkv, *.mpg, *.mp4, *.flv
# (Line 4) icon = video
#
# Line 1 contains the section name.  This is solely for your own reference.
# The special section name 'options' is reserved.
#
# Line 2 contains a command to play files with.  The special term '{file}'
# indicates where the filename should go when executing the command.  Do not
# put quotes around it -- the proper quoting and escaping will be done
# automatically.
#
# Line 3 lists filename patterns, comma-delimited, that this command can play.
# These can also be used to specify entire folders to apply this command to, by
# doing /path/to/folder/*.  Note that these filename patterns use glob-style
# matching, not regular expressions.  So the familiar old wildcards of * and ?
# are what you want to use.  For gritty details on what other special
# characters may go into filename match patterns, run the command 'pydoc
# fnmatch.fnmatch'.
#
# Line 4 states which icon to show for these files.  The only current options
# are 'video', 'game', and 'folder'; though htpicker automatically uses the
# folder icon for directories, so you probably won't have any use for it.
#
# A few reasonable defaults have been put here for you:

[mplayer]
# this -geometry option is highly recommended, otherwise you will often get a
# briefly visible "phantom" mplayer window, before mplayer goes full screen.
command = mplayer -geometry 1x1+4000+4000 -fs {file}
matches = ~/Videos/*, ~/Video/*, *.avi, *.mkv, *.mpg, *.mp4, *.flv, *.divx
icon = video

[zsnes]
command = zsnes {file}
matches = ~/ROMs/SNES/*, *.smc, *.fig, *.zip
icon = game

[fceu]
command = fceu -fs 1 {file}
matches = ~/ROMs/NES/*, *.nes, *.nes.gz
icon = game

# And here is the global options section.
[options]
ignore = .*, *~, *.bak, *.nfo, *.txt, *.url, *.sfv, *.part*.rar
fullscreen = off
"""
