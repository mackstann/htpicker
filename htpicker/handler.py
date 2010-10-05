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
from htpicker.config import NoMatchingSectionForCommand

class HTPickerURLHandler(URLHandler):
    def __init__(self, scheme, config, dir_change_cb):
        super(HTPickerURLHandler, self).__init__(scheme)
        self.config = config
        self.dir_change_cb = dir_change_cb

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
    def show_animations(self):
        return {'show_animations': int(self.config.get_show_animations())}

    @URLAction
    def fullscreen(self):
        return {'fullscreen': int(self.config.get_fullscreen())}

    @URLAction
    def get_initial_dir(self):
        return {'initial_dir': self.config.get_initial_dir()}

    @URLAction
    def file_resource(self, filepath, mime_type):
        # sadly there appears to be no way to sniff the mime type from the
        # Accept header (or access request headers in general), so we must also
        # ask for it in the URL.
        filename = pkg_resources.resource_filename(__name__, 'data/'+filepath)
        return 'file://' + urllib.quote(filename)

    @staticmethod
    def data_uri(data, mime_type, encoding='utf-8'):
        return 'data:{0};charset={1};base64,'.format(mime_type, encoding) + data.encode('base64')

    @classmethod
    def json_data_uri(cls, data):
        return cls.data_uri(json.dumps(data), 'application/json')

    def return_uri_filter(self, data):
        if isinstance(data, types.DictType):
            return self.json_data_uri(data)
        return data

    @URLAction
    def play_file(self, fullpath):
        try:
            command = self.config.get_command(fullpath)
        except NoMatchingSectionForCommand:
            logging.warn("I don't know what command to play this file with: " + fullpath)
            return

        #subprocess.Popen(command, shell=True)
        #os.waitpid(proc.pid, 0)

        # the above "should" work but results in a mysterious situation
        # on my eeepc: mplayer outputs one line ("MPlayer SVN-r29237-4.4.1
        # (C) 2000-2009 MPlayer Team") to the shell, and then everything
        # stops.  mplayer is hung, and htpicker has mysteriously received a
        # SIGSTOP from somewhere.  i don't get it AT ALL.

        # the following is uglier but works just fine.
        os.system(command + ' &')


    @URLAction
    def list_files(self, directory):
        directory = os.path.abspath(directory)
        files = []
        ignores = self.config.get_ignores()
        listing = set(os.listdir(directory))

        # this funky expression filters out all files matching any of the
        # specified of ignore patterns.  it is ugly because it is fast.  see
        # fnmatch_vs_regex.py and file_ignore_algorithms.py in experiments/
        ignore_files = set(itertools.chain(*[fnmatch.filter(listing, ignore) for ignore in ignores]))

        listing.difference_update(ignore_files)
        listing = sorted(listing, key=str.lower)

        for i, filename in enumerate(listing):
            fullpath = directory + '/' + filename

            real = os.path.realpath(os.path.abspath(fullpath))
            try:
                mode = os.stat(real).st_mode
            except OSError:
                # broken symlink, among other things
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
