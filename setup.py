from setuptools import setup, find_packages
setup(
    name = "htpicker",
    version = "0.1.3",
    packages = find_packages(),

    install_requires = ['distribute'],

    package_data = {
        'htpicker': [
            'data/app.html',
            'data/css/htpicker.css',
            'data/js/htpicker.js',
            'data/css/ui-darkness/images/ui-anim_basic_16x16.gif',
            'data/css/ui-darkness/images/ui-bg_flat_30_cccccc_40x100.png',
            'data/css/ui-darkness/images/ui-bg_flat_50_5c5c5c_40x100.png',
            'data/css/ui-darkness/images/ui-bg_glass_20_555555_1x400.png',
            'data/css/ui-darkness/images/ui-bg_glass_40_0078a3_1x400.png',
            'data/css/ui-darkness/images/ui-bg_glass_40_ffc73d_1x400.png',
            'data/css/ui-darkness/images/ui-bg_gloss-wave_25_333333_500x100.png',
            'data/css/ui-darkness/images/ui-bg_highlight-soft_80_eeeeee_1x100.png',
            'data/css/ui-darkness/images/ui-bg_inset-soft_25_000000_1x100.png',
            'data/css/ui-darkness/images/ui-bg_inset-soft_30_f58400_1x100.png',
            'data/css/ui-darkness/images/ui-icons_222222_256x240.png',
            'data/css/ui-darkness/images/ui-icons_4b8e0b_256x240.png',
            'data/css/ui-darkness/images/ui-icons_a83300_256x240.png',
            'data/css/ui-darkness/images/ui-icons_cccccc_256x240.png',
            'data/css/ui-darkness/images/ui-icons_ffffff_256x240.png',
            'data/css/ui-darkness/jquery-ui-1.8.2.custom.css',
            'data/images/nuvola/gamepad.svg',
            'data/images/nuvola/gnome-fs-directory-visiting.svg',
            'data/images/nuvola/mplayer.svg',
            'data/js/jquery-1.4.2.min.js',
            'data/js/jquery-ui-1.8.2.custom.min.js',
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
