from django.utils.translation import ugettext as _

from mezzanine.conf import register_setting


register_setting(
    name="WIKI_DEFAULT_INDEX",
    label=_("Wiki default index page"),
    description=_("Wiki default index page"),
    editable=True,
    default="Main_page",
)

register_setting(
    name="WIKI_USE_FEATURED_IMAGE",
    description=_("Wiki uses featured image"),
    editable=False,
    default=False,
)

register_setting(
    name="WIKI_PAGES_PER_PAGE",
    label=_("Wiki pages per page"),
    description=_("Wiki pages per page"),
    editable=True,
    default=10,
)

register_setting(
    name="WIKI_TEXT_FILTER",
    description=_("Wiki markup language filter"),
    editable=False,
    default="mezzanine_wiki.filters.md_wikilinks",
)

register_setting(
    name="WIKI_TEXT_WIDGET_CLASS",
    description=_("Wiki text widget class"),
    editable=False,
    default="mezzanine_wiki.forms.PlainWidget",
)

WIKI_PRIVACY_OPENED = 1
WIKI_PRIVACY_REGISTERED = 2
WIKI_PRIVACY_MODERATED = 3
WIKI_PRIVACY_CLOSED = 4
WIKI_PRIVACY_CHOICES = (
    (WIKI_PRIVACY_OPENED, _('Opened')),
    (WIKI_PRIVACY_REGISTERED, _('Registered')),
    (WIKI_PRIVACY_MODERATED, _('Moderated')),
    (WIKI_PRIVACY_CLOSED, _('Closed')),
)

register_setting(
    name="WIKI_PRIVACY",
    label=_("Wiki privacy"),
    description=_("Designates who can edit wiki pages"),
    editable=True,
    choices=WIKI_PRIVACY_CHOICES,
    default=WIKI_PRIVACY_REGISTERED,
)
