
from django.conf.urls.defaults import patterns, url


# Wiki patterns.
urlpatterns = patterns("mezawiki.views",
    url("^tag/(?P<tag>.*)/$", "wiki_page_list", name="wiki_page_list_tag"),
    url("^category/(?P<category>.*)/$", "wiki_page_list",
        name="wiki_page_list_category"),
    url("^author/(?P<username>.*)/$", "wiki_page_list",
        name="wiki_page_list_author"),
    url("^(?P<slug>.*)/edit/$", "wiki_page_edit", name="wiki_page_edit"),
    url("^(?P<slug>.*)/$", "wiki_page_detail", name="wiki_page_detail"),
    url("^$", "wiki_page_list", name="wiki_page_list"),
)
