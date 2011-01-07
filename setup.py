from setuptools import setup, find_packages
setup(
    name = "htpicker",
    version = "0.1",
    packages = find_packages(),

    install_requires = ['distribute'],

    package_data = {
        'htpicker': [
            'data/js/*.js',
            'data/css/*.css',
            'data/css/*/*.css',
            'data/css/*/images/*',
            'data/images/*/*',
            'data/app.html',
        ],
    },

    # so we can safely serve data files through file:// URLs
    zip_safe = False,

    entry_points = {
        'console_scripts': ['htpicker = htpicker:main'],
    },

    author = "Nick Welch",
    author_email = "nick@incise.org",
    description = "A simple home theater frontend",
    license = "Public Domain + CC Attribution + LGPL + MIT",
    keywords = "home theater htpc frontend media player",
    url = "http://github.com/mackstann/htpicker",
)
