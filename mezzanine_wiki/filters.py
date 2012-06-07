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
    configs = {'base_url':'/wiki/'}
    wikilinks_extra = WikiLinkExtraExtension(configs=configs)
    return markdown(content,[wikilinks_extra])

