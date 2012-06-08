
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Count

from mezzanine_wiki.models import WikiPage, WikiCategory
from mezzanine import template
from mezzanine.conf import settings
from mezzanine.utils.importing import import_dotted_path


register = template.Library()


@register.as_tag
def wiki_months(*args):
    """
    Put a list of dates for wiki pages into the template context.
    """
    dates = WikiPage.objects.published().values_list("publish_date", flat=True)
    date_dicts = [{"date": datetime(d.year, d.month, 1)} for d in dates]
    month_dicts = []
    for date_dict in date_dicts:
        if date_dict not in month_dicts:
            month_dicts.append(date_dict)
    for i, date_dict in enumerate(month_dicts):
        month_dicts[i]["page_count"] = date_dicts.count(date_dict)
    return month_dicts


@register.as_tag
def wiki_categories(*args):
    """
    Put a list of categories for wiki pages into the template context.
    """
    pages = WikiPage.objects.published()
    categories = WikiCategory.objects.filter(wikipages__in=pages)
    return list(categories.annotate(page_count=Count("wikipages")))


@register.as_tag
def wiki_authors(*args):
    """
    Put a list of authors (users) for wiki pages into the template context.
    """
    wiki_pages = WikiPage.objects.published()
    authors = User.objects.filter(wikipages__in=wiki_pages)
    return list(authors.annotate(post_count=Count("wikipages")))


@register.as_tag
def wiki_recent_pages(limit=5):
    """
    Put a list of recently published wiki pages into the template context.
    """
    return list(WikiPage.objects.published().order_by('-publish_date')[:limit])


@register.filter
def wikitext_filter(content):
    """
    This template filter takes a string value and passes it through the
    function specified by the WIKI_TEXT_FILTER setting.
    """
    if settings.WIKI_TEXT_FILTER:
        func = import_dotted_path(settings.WIKI_TEXT_FILTER)
    else:
        func = lambda s: s
    return func(content)

