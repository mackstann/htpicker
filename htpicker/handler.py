#!/usr/bin/env python

import os
import fnmatch
import json
import pipes
import pkg_resources
import stat
import subprocess
import sys
import types
import urllib

from htpicker.browser import URLHandler, URLAction

class MyHandler(URLHandler):
    def __init__(self, scheme, config):
        super(MyHandler, self).__init__(scheme)
        self.config = config

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
    def get_initial_dir(self):
        d = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
        return {'initial_dir': d}

    @URLAction
    def execute(self, section, fullpath):
        kw = {'file': pipes.quote(fullpath)}
        command = self.config.get_default(section, 'command', '', **kw)
        if not command:
            print "You need to define a command for '{0}'".format(section)
        else:
            subprocess.Popen(command, shell=True)


    def section_for_file(self, fullpath):
        for section in self.config.sections():
            folders = self.config.get_list(section, 'folders', [])
            for folder in folders:
                if is_child_of(folder, fullpath):
                    return section

        # okay, didn't find it in a folder, so check the patterns

        for section in self.config.sections():
            patterns = self.config.get_list(section, 'matches', [])
            for pattern in patterns:
                if fnmatch.fnmatch(fullpath, pattern):
                    return section

    @URLAction
    def play_file(self, fullpath):
        section = self.section_for_file(fullpath)
        if section:
            self.execute(section, fullpath)
        else:
            print "i don't know what command to play this file with: ", fullpath

    @URLAction
    def list_files(self, directory):
        directory = os.path.abspath(directory)

        files = []

        ignores = self.config.get_list('options', 'ignore', [])

        listing = sorted([
            filename for filename in os.listdir(directory)
            if not any(fnmatch.fnmatch(filename, ignore) for ignore in ignores)
        ], key=str.lower)

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
                section = self.section_for_file(fullpath)
                if section:
                    icon = self.config.get_default(section, 'icon', '')
                else:
                    icon = ''
            else:
                filetype = 'other'


            files.append({
                'fullpath': fullpath,
                'display_name': (os.path.splitext(filename)[0]
                                 if filetype == 'file' else filename),
                'type': filetype,
                'icon': icon,
            })

        files.insert(0, {
            'fullpath': '/' + directory.rsplit('/', 1)[0].lstrip('/'),
            'display_name': '&#8593; Parent Folder',
            'type': 'directory',
            'icon': 'directory',
        })

        return { 'files': files }

def is_child_of(dir_in_question, filename):
    d = dir_in_question.rstrip('/') + '/'
    f = filename
    real = os.path.realpath
    common = os.path.commonprefix

    # try both given path and real path for both directory and file.
    if d == common([d, f]): return True
    if d == common([real(d), f]): return True
    if d == common([d, real(f)]): return True
    if d == common([real(d), real(f)]): return True
