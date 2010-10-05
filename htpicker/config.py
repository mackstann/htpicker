#!/usr/bin/env python

import ConfigParser
import fnmatch
import logging
import os
import pipes

class MyConfigParser(ConfigParser.RawConfigParser):
    def get_default(self, section, option, default):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return default

    def getboolean_default(self, section, option, default):
        try:
            return ConfigParser.RawConfigParser.getboolean(self, section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return default

    def getlist(self, section, option):
        val = self.get_default(section, option, '')
        if not val:
            return []
        return map(str.strip, val.split(','))

class NoMatchingSectionForCommand(Exception): pass

class HTPickerConfig(MyConfigParser):
    def __init__(self, filename, argv):
        MyConfigParser.__init__(self)

        if not os.path.isfile(filename):
            write_default_config(filename)
            logging.info("I have created a ~/.htpickerrc config file for you.  "
                    "Take a look and edit it to your liking.")

        if not self.has_section('options'):
            self.add_section('options')

        if len(argv) > 1:
            self.set('options', 'initial_dir', argv[1])
        elif self.get_default('options', 'initial_dir', None) is None:
            self.set('options', 'initial_dir', os.getcwd())

        self.read(filename)

    def get_fullscreen(self):
        return self.getboolean_default('options', 'fullscreen', False)

    def get_show_animations(self):
        return self.getboolean_default('options', 'animations', True)

    def get_command(self, file_path):
        section = self._section_for_file(file_path)
        if not section:
            raise NoMatchingSectionForCommand()
        return self.get_default(section, 'command', '').format(file=pipes.quote(file_path))

    def get_icon(self, file_path):
        section = self._section_for_file(file_path)
        if section:
            return self.get_default(section, 'icon', '')
        return ''

    def _section_for_file(self, file_path):
        for section in self.sections():
            patterns = self.getlist(section, 'matches')
            for pattern in patterns:
                pattern = os.path.expanduser(pattern)
                if fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                    return section


def write_default_config(filename):
    f = open(filename, 'w')
    f.write(default_config)
    f.close()

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
# Line 4 (optional) states which icon to show for these files.  The only
# current options are 'video', 'game', and 'folder'; though htpicker
# automatically uses the folder icon for directories, so you probably won't
# have any use for it.
#
# A few reasonable defaults have been put here for you:

[mplayer]
# this -geometry option is highly recommended, otherwise you will often get a
# briefly visible "phantom" mplayer window, before mplayer goes full screen.
command = mplayer -geometry 1x1+4000+4000 -fs {file}
matches = ~/Videos/*, ~/Video/*, *.avi, *.mkv, *.mpg, *.mp4, *.flv, *.divx, *.wmv
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
animations = on

# if you set this, htpicker will start in the specified directory.  if you pass
# a directory name on the command line, though, it will override this setting.
#initial_dir = /path/to/somewhere
"""
