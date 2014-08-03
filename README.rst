========
Overview
========

Wiki application for Mezzanine.

Features:

- markdown syntax with [[Wiki links]] extension
- page history and diff viewing

Requirements:

- mezzanine >= 3.1
- markdown
- diff-match-patch
- south


=========
Mezzanine
=========

Mezzanine is a content management platform built using the Django
framework. It is BSD licensed and designed to provide both a
consistent interface for managing content, and a simple, extensible
architecture that makes diving in and hacking on the code as easy as
possible.

Visit the Mezzanine project page to see some of the great sites
people have built using Mezzanine.

http://mezzanine.jupo.org

http://github.com/stephenmcd/mezzanine


===========
Quick start
===========

1. Add "mezzanine_wiki" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'mezzanine_wiki',
    )
    
2. Add "mezzanine_wiki.WikiPage" to SEARCH_MODEL_CHOICES setting like this:

    SEARCH_MODEL_CHOICES = ('pages.Page', 'blog.BlogPost', 'mezzanine_wiki.WikiPage')

3. Include the wiki URLconf in your project urls.py like this::

    url(r'^wiki/', include('mezzanine_wiki.urls')),

4. Run `python manage.py migrate` to create the wiki models.

5. Restart server.

6. Visit /wiki/ to use the wiki. 
