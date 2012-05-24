from django.utils.translation import ugettext as _

from mezzanine.conf import register_setting


register_setting(
    name="WIKI_USE_FEATURED_IMAGE",
    description=_("."),
    editable=False,
    default=False,
)

register_setting(
    name="WIKI_PAGES_PER_PAGE",
    description=_("."),
    editable=False,
    default=10,
)

register_setting(
    name="WIKI_MARKUP_LANGUAGE",
    description=_("."),
    editable=False,
    default="creole",
)

