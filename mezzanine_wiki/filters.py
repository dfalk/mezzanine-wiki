from django.core.urlresolvers import reverse
from markdown import markdown
from mezzanine_wiki.mdx_wikilinks_extra import WikiLinkExtraExtension


def md_plain(content):
    """
    Renders content using markdown.
    """
    return markdown(content)


def md_wikilinks(content):
    """
    Renders content using markdown with wikilinks.
    Format: [[link|optional label]]
    """
    base_url = reverse('wiki_index')
    configs = {'base_url': base_url}
    wikilinks_extra = WikiLinkExtraExtension(configs=configs)
    return markdown(content,[wikilinks_extra])

