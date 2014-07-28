========
Overview
========

Wiki application for Mezzanine.


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

2. Include the polls URLconf in your project urls.py like this::

    url(r'^wiki/', include('mezzanine_wiki.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/wiki/
   to create a wiki page.

5. Visit http://127.0.0.1:8000/wiki/ to participate in the poll.