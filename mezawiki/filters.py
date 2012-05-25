import markdown
from mezawiki.mdx_wikilinks_extra import WikiLinkExtraExtension
from mezawiki.mdx_wikilinks_extra import build_url


def md_plain(content):
    """
    Renders content using markdown.
    """
    return markdown.markdown(content)


def md_wikilinks(content):
    """
    Renders content using markdown with wikilinks.
    Format: [[link|optional label]]
    """
    configs = {'base_url':'/wiki/'}
    wikilinks_extra = WikiLinkExtraExtension(configs=configs)
    return markdown.markdown(content,[wikilinks_extra])
    #return md.convert(content)

