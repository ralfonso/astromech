#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u"Ryan Roemmich"
SITENAME = u"Astromech"
SITEURL = ''

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Blogroll
LINKS =  (('Pelican', 'http://docs.notmyidea.org/alexis/pelican/'),
          ('Python.org', 'http://python.org'),
          ('Jinja2', 'http://jinja.pocoo.org'),
          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}.html'

DIRECT_TEMPLATES = ('index', )
DEFAULT_PAGINATION = False

THEME = './themes/r2'

TYPOGRIFY = True
