
from django.conf.urls.defaults import patterns, url


# Wiki patterns.
urlpatterns = patterns("mezzanine_wiki.views",
    url("^$", "wiki_index", name="wiki_index"),
    url("^list:pages/$", "wiki_page_list", name="wiki_page_list"),
    url("^tag:(?P<tag>.*)/$", "wiki_page_list", name="wiki_page_list_tag"),
    url("^category:(?P<category>.*)/$", "wiki_page_list",
        name="wiki_page_list_category"),
    url("^author:(?P<username>.*)/$", "wiki_page_list",
        name="wiki_page_list_author"),
    url("^(?P<slug>.*)/history/$", "wiki_page_history",
        name="wiki_page_history"),
    url("^(?P<slug>.*)/history/(?P<rev_id>\d+)/$", "wiki_page_revision",
        name="wiki_page_revision"),
    url("^(?P<slug>.*)/edit/$", "wiki_page_edit", name="wiki_page_edit"),
    url("^(?P<slug>.*)/$", "wiki_page_detail", name="wiki_page_detail"),
)
