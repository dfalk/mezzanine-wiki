from django.utils.translation import ugettext as _

from mezzanine.conf import register_setting


register_setting(
    name="WIKI_DEFAULT_INDEX",
    description=_("Wiki default index page"),
    editable=False,
    default="MainPage",
)

register_setting(
    name="WIKI_USE_FEATURED_IMAGE",
    description=_("Wiki uses featured image"),
    editable=False,
    default=False,
)

register_setting(
    name="WIKI_PAGES_PER_PAGE",
    description=_("Wiki pages per page"),
    editable=True,
    default=10,
)

register_setting(
    name="WIKI_TEXT_FILTER",
    description=_("Wiki markup language filter"),
    editable=False,
    default="mezawiki.filters.md_wikilinks",
)

register_setting(
    name="WIKI_TEXT_WIDGET_CLASS",
    description=_("Wiki text widget class"),
    editable=False,
    default="mezawiki.forms.PlainWidget",
)

