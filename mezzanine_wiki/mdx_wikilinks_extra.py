#!/usr/bin/env python

'''
WikiLinks Extra Extension for Python-Markdown
=============================================

Converts [[WikiLinks|label text]] to relative links.
Requires Python-Markdown 2.0+

Original extension wikilinks By [Waylan Limberg](http://achinghead.com/).

License: [BSD](http://www.opensource.org/licenses/bsd-license.php) 

Dependencies:
* [Python 2.5+](http://python.org)
* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)
'''

import markdown
import re

def build_url(label, base, end):
    """ Build a url from the label, a base, and an end. """
    clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '%s%s%s'% (base, clean_label, end)


class WikiLinkExtraExtension(markdown.Extension):
    def __init__(self, configs):
        # set extension defaults
        self.config = {
            'base_url' : ['/', 'String to append to beginning or URL.'],
            'end_url' : ['/', 'String to append to end of URL.'],
            'html_class' : ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url' : [build_url, 'Callable formats URL from label.'],
        }
        
        # Override defaults with user settings
        for key, value in configs.iteritems():
            self.setConfig(key, value)
        
    def extendMarkdown(self, md, md_globals):
        self.md = md

        # Pattern for wikilinks extended format [[link|label]]
        WIKILINK_RE = r'\[\[([\w0-9_ -]+)(\|([\w0-9_ - ]+))?\]\]'
        wikilinkPattern = WikiLinksExtra(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        # append to end of inline patterns
        md.inlinePatterns.add('wikilink', wikilinkPattern, "<not_strong")


class WikiLinksExtra(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern, config):
        markdown.inlinepatterns.Pattern.__init__(self, pattern)
        self.config = config
  
    def handleMatch(self, m):
        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()
            label = m.group(2).strip()
            url = self.config['build_url'](label, base_url, end_url)
            a = markdown.util.etree.Element('a')
            if m.group(4):
                a.text = m.group(4).strip()
            else:
                a.text = label
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a

    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if self.md.Meta.has_key('wiki_base_url'):
                base_url = self.md.Meta['wiki_base_url'][0]
            if self.md.Meta.has_key('wiki_end_url'):
                end_url = self.md.Meta['wiki_end_url'][0]
            if self.md.Meta.has_key('wiki_html_class'):
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class
    

def makeExtension(configs=None) :
    return WikiLinkExtraExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

