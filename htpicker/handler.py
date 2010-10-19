#!/usr/bin/env python

import os
import fnmatch
import itertools
import json
import logging
import pkg_resources
import stat
import types
import urllib

from htpicker.browser import URLHandler, URLAction

class HTPickerURLHandler(URLHandler):
    def __init__(self, scheme, config, dir_change_cb):
        super(HTPickerURLHandler, self).__init__(scheme)
        self.config = config
        self.dir_change_cb = dir_change_cb

    def return_uri_filter(self, data):
        if isinstance(data, types.DictType):
            return ('data:application/json;charset=utf-8;base64,'
                    + json.dumps(data).encode('base64'))
        return data

    @URLAction
    def exit(self):
        raise SystemExit

    @URLAction
    def enable_fullscreen(self):
        self.browser.fullscreen()

    @URLAction
    def disable_fullscreen(self):
        self.browser.unfullscreen()

    @URLAction
    def get_startup_config(self):
        return {
            'show_animations': int(self.config.get_show_animations()),
            'fullscreen': int(self.config.get_fullscreen()),
            'initial_dir': os.path.abspath(self.config.get_initial_dir()),
        }

    @URLAction
    def file_resource(self, filepath, mime_type):
        # sadly there appears to be no way to sniff the mime type from the
        # Accept header (or access request headers in general), so we must also
        # ask for it in the URL.
        filename = pkg_resources.resource_filename(__name__, 'data/'+filepath)
        return 'file://' + urllib.quote(filename)

    @URLAction
    def play_file(self, fullpath):
        command = self.config.get_command(fullpath)

        if not command:
            logging.warn("No command is set for this file: " + fullpath)
            return

        os.system(command + ' &')

        #subprocess.Popen(command, shell=True)
        #os.waitpid(proc.pid, 0)

        # the above "should" work but results in a mysterious situation
        # on my eeepc: mplayer outputs one line ("MPlayer SVN-r29237-4.4.1
        # (C) 2000-2009 MPlayer Team") to the shell, and then everything
        # stops.  mplayer is hung, and htpicker has mysteriously received a
        # SIGSTOP from somewhere.  i don't get it AT ALL.

        # system(command + ' &') is ugly but works fine.


    @URLAction
    def list_files(self, directory):
        files = []

        ignore_match = self.config.get_ignore_regex().match

        listing = [ f for f in os.listdir(directory) if not ignore_match(f.lower()) ]
        listing = sorted(listing, key=str.lower)

        for filename in listing:
            fullpath = directory + '/' + filename

            try:
                mode = os.stat(fullpath).st_mode
            except OSError: # broken symlink, among other things
                continue

            if stat.S_ISDIR(mode):
                filetype = 'directory'
                icon = 'directory'
            elif stat.S_ISREG(mode):
                filetype = 'file'
                icon = self.config.get_icon(fullpath)
            else:
                filetype = 'other'


            files.append({
                'fullpath': fullpath,
                'display_name': (os.path.splitext(filename)[0]
                                 if filetype == 'file' else filename),
                'type': filetype,
                'icon': icon,
            })

        if directory != '/':
            files.insert(0, {
                'fullpath': '/' + directory.rsplit('/', 1)[0].lstrip('/'),
                'display_name': '&#8593; Parent Folder',
                'type': 'directory',
                'icon': 'directory',
            })

        self.dir_change_cb(directory)

        return { 'files': files }
