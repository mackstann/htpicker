#!/usr/bin/env python

import ConfigParser
import fnmatch
import gtk
import json
import os
import pipes
import stat
import subprocess
import sys
import urlparse
import webkit
import pkg_resources

class RequestInterceptingWebView(webkit.WebView):
    def __init__(self, url_handler_cb, url=None, content=None, mime_type=None, encoding=None, base_uri=None):
        super(RequestInterceptingWebView, self).__init__()
        self.url_handler_cb = url_handler_cb

        self.connect('resource-request-starting', self._resource_cb)
        if url is not None:
            self.open(url)
        else:
            self.load_string(content, mime_type, encoding, base_uri)

        settings = self.get_settings()

        settings_values = (
            ("enable-default-context-menu",           False, '1.1.18'),
            ("enable-java-applet",                    False, '1.1.22'),
            ("enable-plugins",                        False, '???'   ),
            ("enable-universal-access-from-file-uris", True, '1.1.13'),
            ("enable-xss-auditor",                    False, '1.1.11'),
            ("tab-key-cycles-through-elements",       False, '1.1.17'),
        )

        for key, val, version in settings_values:
            try:
                settings.set_property(key, val)
            except TypeError:
                print "Your version of WebKit does not support the setting '{0}'.".format(key)
                print "This setting requires version {0}.".format(version)
                print "For best compatibility, use at least version 1.1.22."
                print

    def _resource_cb(self, view, frame, resource, request, response):
        self.url_handler_cb(request)

class WebBrowser(gtk.Window):
    def __init__(self, url_handler_cb, **kw):
        gtk.Window.__init__(self)

        self.connect('destroy', self._destroy_cb)
        self.set_default_size(800, 600)

        web_view = RequestInterceptingWebView(url_handler_cb, **kw)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        self.add(scrolled_window)
        self.show_all()

    def _destroy_cb(self, window):
        window.destroy()
        gtk.main_quit()

class URLHandler(object):
    """
    A URL Handler for a given network scheme.

    This assumes URIs of the form "scheme://method".  If you register with the
    scheme "foo", then the URI "foo://bar" will call your bar() method.

    Query string parameters will be translated into Python keyword arguments
    and passed to your method.  If you use a query parameter more than once,
    the multiple values will be rolled up into a list.  E.g:

        yourapp://yourmethod?a=one&a=two&b=three

    will become:

        yourmethod(a=['one', 'two'], b='three')
    """

    def __init__(self, scheme):
        self.scheme = scheme

    def return_uri_filter(self, uri):
        return uri

    def handle_request(self, request):
        # i don't use urlparse.urlsplit() because it doesn't parse the
        # netloc/path of non-http:// URLs in the usual way.
        uri = request.get_uri()

        if not uri.startswith(self.scheme+'://'):
            return

        scheme, rest = uri.split('://', 1)

        if '?' in rest:
            action, qs = rest.split('?')
        else:
            action = rest
            qs = ''

        q = urlparse.parse_qs(qs)

        params = {}
        for key, values in q.items():
            params[key] = values[0] if len(values) == 1 else values

        ret = getattr(self, action)(**params)

        if hasattr(self, 'return_uri_filter'):
            new_uri = self.return_uri_filter(ret)
        else:
            new_uri = ret

        if new_uri:
            request.set_uri(new_uri)

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
command = mplayer -fs {file}
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
ignore = *~, *.bak, *.nfo, *.txt, *.url, *.sfv, *.part*.rar
fullscreen = off
"""

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

    def get_list(self, section, option, default, **kwargs):
        val = self.get_default(section, option, default, **kwargs)

        # the default is passed as a list type, so don't text-manipulate it.
        if val == default:
            return default

        return map(str.strip, val.split(','))


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

class MyHandler(URLHandler):
    def __init__(self, scheme, config):
        super(MyHandler, self).__init__(scheme)
        self.config = config

    @staticmethod
    def json_data_uri(data):
        return 'data:application/json;charset=utf-8;base64,' + json.dumps(data).encode('base64')

    def return_uri_filter(self, data):
        return self.json_data_uri(data)

    def get_initial_dir(self):
        d = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
        return {'initial_dir': d}

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

    def play_file(self, fullpath):
        section = self.section_for_file(fullpath)
        if section:
            self.execute(section, fullpath)
        else:
            print "i don't know what command to play this file with: ", fullpath

    def list_files(self, directory):
        base = os.path.abspath(directory)

        files = []

        ignores = self.config.get_list('options', 'ignore', [])
        for i, filename in enumerate(sorted(os.listdir(base))):
            if filename.startswith('.'):
                continue

            nextfile = False
            for ignore in ignores:
                if fnmatch.fnmatch(filename, ignore):
                    # crude multi-level loop continue
                    nextfile = True
                    break

            if nextfile:
                continue

            fullpath = base + '/' + filename

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
            'fullpath': base + '/' + '..',
            'display_name': '&#8593; Parent Folder',
            'type': 'directory',
            'icon': 'directory',
        })

        return { 'files': files }

# bug! alert() hangs the app... sometimes

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

def main():
    gtk.gdk.threads_init()

    config = load_config()

    handler = MyHandler('htpicker', config)

    html = pkg_resources.resource_string(__name__, 'data/app.html')

    webbrowser = WebBrowser(handler.handle_request, content=html,
            mime_type='text/html', encoding='utf-8', base_uri='file://')

    if config.getboolean_default('options', 'fullscreen', '0'):
        webbrowser.fullscreen()

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
