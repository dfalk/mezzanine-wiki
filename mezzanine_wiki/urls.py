
from django.conf.urls.defaults import patterns, url


# Wiki patterns.
urlpatterns = patterns("mezzanine_wiki.views",
    url("^$", "wiki_index", name="wiki_index"),
    url("^pages:new/$", "wiki_page_new", name="wiki_page_new"),
    url("^pages:list/$", "wiki_page_list", name="wiki_page_list"),
    url("^pages:changes/$", "wiki_page_changes", name="wiki_page_changes"),
    url("^tag:(?P<tag>.*)/$", "wiki_page_list", name="wiki_page_list_tag"),
    url("^category:(?P<category>.*)/$", "wiki_page_list",
                                              name="wiki_page_list_category"),
    url("^author:(?P<username>.*)/$", "wiki_page_list",
                                              name="wiki_page_list_author"),
    url("^(?P<slug>.*)/history/$", "wiki_page_history",
                                              name="wiki_page_history"),
    url("^(?P<slug>.*)/history/(?P<rev_id>\d+)/$", "wiki_page_revision",
                                              name="wiki_page_revision"),
    url("^(?P<slug>.*)/diff/$", "wiki_page_diff",
                                              name="wiki_page_diff"),
    url("^(?P<slug>.*)/revert/(?P<revision_pk>[0-9]+)/$", "wiki_page_revert",
                                              name="wiki_page_revert"),
    url("^(?P<slug>.*)/undo/(?P<revision_pk>[0-9]+)/$", "wiki_page_undo",
                                              name="wiki_page_undo"),
    url("^(?P<slug>.*)/edit/$", "wiki_page_edit", name="wiki_page_edit"),
    url("^(?P<slug>.*)/$", "wiki_page_detail", name="wiki_page_detail"),
)
