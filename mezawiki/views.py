from calendar import month_name
from collections import defaultdict

from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django import VERSION

from mezawiki.models import WikiPage, WikiCategory
#from mezzanine.blog.feeds import PostsRSS, PostsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import AssignedKeyword, Keyword
from mezzanine.utils.views import render, paginate
from mezawiki.forms import WikiPageForm


def wiki_page_list(request, tag=None, username=None,
                   category=None, template="mezawiki/wiki_page_list.html"):
    """
    Display a list of wiki pages that are filtered by tag, 
    author or category. Custom templates are checked for using the name
    ``mezawiki/wiki_page_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    settings.use_editable()
    templates = []
    wiki_pages = WikiPage.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        wiki_pages = wiki_pages.filter(keywords__in=tag.assignments.all())
    if category is not None:
        category = get_object_or_404(WikiCategory, slug=category)
        wiki_pages = wiki_pages.filter(categories=category)
        templates.append(u"mezawiki/wiki_post_list_%s.html" %
                          unicode(category.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        wiki_pages = wiki_pages.filter(user=author)
        templates.append(u"mezawiki/wiki_page_list_%s.html" % username)

    # We want to iterate keywords and categories for each wiki page
    # without triggering "num posts x 2" queries.
    #
    # For Django 1.3 we create dicts mapping wiki page IDs to lists of
    # categories and keywords, and assign these to each wiki page
    #
    # For Django 1.4 we just use prefetch related.

    if VERSION >= (1, 4):
        rel = ("categories", "keywords__keyword")
        wiki_pages = wiki_pages.select_related("user").prefetch_related(*rel)
    else:
        wiki_pages = list(wiki_pages.select_related("user"))
        categories = defaultdict(list)
        if wiki_pages:
            ids = ",".join([str(p.id) for p in wiki_pages])
            for cat in WikiCategory.objects.raw(
                "SELECT * FROM mezawiki_wikicategory "
                "JOIN mezawiki_wikipage_categories "
                "ON mezawiki_wikicategory.id = wikicategory_id "
                "WHERE wikipage_id IN (%s)" % ids):
                categories[cat.wikipage_id].append(cat)
        keywords = defaultdict(list)
        wikipage_type = ContentType.objects.get(app_label="mezawiki",
                                                model="wikipage")
        assigned = AssignedKeyword.objects.filter(wikipage__in=wiki_pages,
                        content_type=wikipage_type).select_related("keyword")
        for a in assigned:
            keywords[a.object_pk].append(a.keyword)
    for i, page in enumerate(wiki_pages):
        if VERSION < (1, 4):
            setattr(wiki_pages[i], "category_list", categories[page.id])
            setattr(wiki_pages[i], "keyword_list", keywords[page.id])
        else:
            setattr(wiki_pages[i], "category_list",
                    page.categories.all())
            setattr(wiki_pages[i], "keyword_list",
                    [k.keyword for k in page.keywords.all()])

    wiki_pages = paginate(wiki_pages,
                          request.GET.get("page", 1),
                          settings.WIKI_PAGES_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"wiki_pages": wiki_pages,
               "tag": tag, "category": category, "author": author}
    templates.append(template)
    return render(request, templates, context)


def wiki_page_detail(request, slug, year=None, month=None,
                     template="mezawiki/wiki_page_detail.html"):
    """. Custom templates are checked for using the name
    ``mezawiki/wiki_page_detail_XXX.html`` where ``XXX`` is the wiki
    pages's slug.
    """
    wiki_pages = WikiPage.objects.published(for_user=request.user)
    wiki_page = get_object_or_404(wiki_pages, slug=slug)
    context = {"wiki_page": wiki_page}
    templates = [u"mezawiki/wiki_page_detail_%s.html" % unicode(slug), template]
    return render(request, templates, context)


def wiki_page_edit(request, slug, 
                     template="mezawiki/wiki_page_edit.html"):
    """. Custom templates are checked for using the name
    ``mezawiki/wiki_page_edit_XXX.html`` where ``XXX`` is the wiki
    pages's slug.
    """

    wiki_pages = WikiPage.objects.published(for_user=request.user)
    wiki_page = get_object_or_404(wiki_pages, slug=slug)

    if request.method == 'POST': # If the form has been submitted...
        form = WikiPageForm(request.POST, instance=wiki_page)
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            form.save()
            return HttpResponseRedirect(reverse('wiki_page_detail', args=[slug])) # Redirect after POST
    else:
        form = WikiPageForm(instance=wiki_page)

    context = {"wiki_page": wiki_page, 'form': form}
    templates = [u"mezawiki/wiki_page_edit_%s.html" % unicode(slug), template]
    return render(request, templates, context)


