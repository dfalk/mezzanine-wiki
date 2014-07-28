from calendar import month_name
from collections import defaultdict

from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django import VERSION
from django.utils.translation import ugettext as _

from mezzanine_wiki.models import WikiPage, WikiCategory, WikiPageRevision
from mezzanine.conf import settings
from mezzanine.generic.models import AssignedKeyword, Keyword
from mezzanine.utils.views import render, paginate
from mezzanine_wiki.forms import WikiPageForm
from mezzanine_wiki.utils import urlize_title, deurlize_title
from mezzanine_wiki import defaults as wiki_settings
from diff_match_patch import diff_match_patch
from urllib import urlencode, quote


def wiki_index(request, template_name='mezawiki/wiki_page_detail.html'):
    """
    Redirects to the default wiki index name.
    """
    if settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_CLOSED:
        return HttpResponseRedirect(reverse('wiki_page_list'))
    return HttpResponseRedirect(
            reverse('wiki_page_detail', args=[settings.WIKI_DEFAULT_INDEX]))


def wiki_page_list(request, tag=None, username=None,
                   category=None, template="mezawiki/wiki_page_list.html"):
    """
    Display a list of wiki pages that are filtered by tag, 
    author or category.

    Custom templates are checked for using the name
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
                "SELECT * FROM mezzanine_wiki_wikicategory "
                "JOIN mezzanine_wiki_wikipage_categories "
                "ON mezzanine_wiki_wikicategory.id = wikicategory_id "
                "WHERE wikipage_id IN (%s)" % ids):
                categories[cat.wikipage_id].append(cat)
        keywords = defaultdict(list)
        wikipage_type = ContentType.objects.get(app_label="mezzanine_wiki",
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
    """
    Displays a wiki page.
    Redirects to the edit view if the page doesn't exist.

    Custom templates are checked for using the name
    ``mezawiki/wiki_page_detail_XXX.html``
    where ``XXX`` is the wiki pages's slug.
    """
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_detail', args=[slug])
        )
    try:
        wiki_page_exist = WikiPage.objects.get(slug=slug)
        if wiki_page_exist.status == 1 and not wiki_page_exist.can_edit_wikipage(request.user):
            return HttpResponseForbidden(
                _("You don't have permission to view this wiki page."))
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
    except WikiPage.DoesNotExist:
        if can_add_wikipage(request.user):
            return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
        else:
            return HttpResponseForbidden(
                _("You don't have permission to add new wiki page."))
    context = {"wiki_page": wiki_page}
    templates = [u"mezawiki/wiki_page_detail_%s.html" % unicode(slug), template]
    return render(request, templates, context)


def wiki_page_history(request, slug,
                     template="mezawiki/wiki_page_history.html"):
    """
    Displays a wiki page history.
    Redirects to the edit view if the page doesn't exist.

    Custom templates are checked for using the name
    ``mezawiki/wiki_page_detail_XXX.html``
    where ``XXX`` is the wiki pages's slug.
    """
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_history', args=[slug])
        )
    try:
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
        revisions = WikiPageRevision.objects.filter(page=wiki_page)
    except WikiPage.DoesNotExist:
        return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
    if not wiki_page.can_view_wikipage(request.user):
        return HttpResponseForbidden(
            _("You don't have permission to view this wiki page."))
    context = {"wiki_page": wiki_page, "revisions": revisions}
    templates = [u"mezawiki/wiki_page_history_%s.html" % unicode(slug), template]
    return render(request, templates, context)


def wiki_page_revision(request, slug, rev_id,
                     template="mezawiki/wiki_page_revision.html"):
    """
    Displays a wiki page revision.
    Redirects to the edit view if the page doesn't exist.

    Custom templates are checked for using the name
    ``mezawiki/wiki_page_detail_XXX.html``
    where ``XXX`` is the wiki pages's slug.
    """
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_revision', args=[slug])
        )
    try:
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
        revision = WikiPageRevision.objects.get(id=rev_id)
    except WikiPage.DoesNotExist:
        return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
    if not wiki_page.can_view_wikipage(request.user):
        return HttpResponseForbidden(
            _("You don't have permission to view this wiki page revision."))
    context = {"wiki_page": wiki_page, "revision": revision}
    templates = [u"mezawiki/wiki_page_detail_%s.html" % unicode(slug), template]
    return render(request, templates, context)


def wiki_page_diff(request, slug,
                     template="mezawiki/wiki_page_diff.html"):
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_diff', args=[slug])
        )
    try:
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
    except WikiPage.DoesNotExist:
        return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
    try:
        from_rev = wiki_page.wikipagerevision_set.get(pk=request.REQUEST['from_revision_pk'])
        to_rev = wiki_page.wikipagerevision_set.get(pk=request.REQUEST['to_revision_pk'])
    except (KeyError, WikiPage.DoesNotExist):
        return HttpResponseNotFound()
    dmp = diff_match_patch()
    diff = dmp.diff_compute(from_rev.content, to_rev.content, True, 2)
    undo_error = False
    if 'undo' in request.REQUEST and request.REQUEST['undo'] == 'error':
        undo_error = True
    return render(request, 'mezawiki/wiki_page_diff.html',
                  {'wiki_page': wiki_page, 'from_revision': from_rev, 'to_revision': to_rev, 'diff': diff, 'undo_error': undo_error})


def wiki_page_revert(request, slug, revision_pk):
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_revert', args=[slug, revision_pk])
        )
    try:
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
    except WikiPage.DoesNotExist:
        return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
    src_revision = get_object_or_404(WikiPageRevision, page=wiki_page, pk=revision_pk)
    new_revision = WikiPageRevision(page=wiki_page,
            user=request.user if request.user.is_authenticated() else User.objects.get(id=-1))
    if request.method == 'POST':
        form = WikiPageForm(data=request.POST or None, instance=wiki_page)
        if form.is_valid():
            form.save()
            new_revision.content = form.cleaned_data["content"]
            new_revision.description = form.cleaned_data["summary"]
            new_revision.save()
            return HttpResponseRedirect(reverse('wiki_page_detail', kwargs={'slug': slug}))
    else:
        if src_revision.user:
            description = _("Reverted to revision of %(time)s by %(user)s.") % \
                    {'time': src_revision.created, 'user': src_revision.user.username}
        else:
            description = _("Reverted to anonymous revision of %(time)s.") % \
                    {'time': src_revision.created}
        form = WikiPageForm(data=request.POST or None, instance=wiki_page,
                initial={'content': src_revision.content, 'summary': description})
    return render(request, 'mezawiki/wiki_page_edit.html',
                  {'wiki_page': wiki_page, 'form': form, 'src_revision': src_revision})


def wiki_page_undo(request, slug, revision_pk):
    slug_original = slug
    slug = urlize_title(slug)
    if slug != slug_original:
        return HttpResponseRedirect(
            reverse('wiki_page_undo', args=[slug, revision_pk])
        )
    try:
        wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = wiki_pages.get(slug=slug)
    except WikiPage.DoesNotExist:
        return HttpResponseRedirect(reverse('wiki_page_edit', args=[slug]))
    src_revision = get_object_or_404(WikiPageRevision, page=wiki_page, pk=revision_pk)
    new_revision = WikiPageRevision(page=wiki_page,
            user=request.user if request.user.is_authenticated() else User.objects.get(id=-1))
    if request.method == 'POST':
        form = WikiPageForm(data=request.POST or None, instance=wiki_page)
        if form.is_valid():
            form.save()
            new_revision.content = form.cleaned_data["content"]
            new_revision.description = form.cleaned_data["summary"]
            new_revision.save()
            return HttpResponseRedirect(reverse('wiki_page_detail', kwargs={'slug': slug}))
    else:
        if src_revision.user:
            description = _("Undid revision of %(time)s by %(user)s.") % \
                    {'time': src_revision.created, 'user': src_revision.user.username}
        else:
            description = _("Undid anonymous revision of %(time)s.") % {'time': src_revision.created}
        prev_revision = None
        try:
            prev_revision = WikiPageRevision.objects\
                    .filter(page=wiki_page, created__lt=src_revision.created)\
                    .order_by('-created')[0]
            prev_content = prev_revision.content
        except IndexError:
            prev_content = ''
        dmp = diff_match_patch()
        rdiff = dmp.patch_make(src_revision.content, prev_content)
        content, results = dmp.patch_apply(rdiff, wiki_page.content)
        if False in results:
            urldata = {'to_revision_pk': src_revision.pk}
            if prev_revision:
                urldata['from_revision_pk'] = prev_revision.pk
            urldata['undo'] = 'error'
            return HttpResponseRedirect("%s?%s" % (
                    reverse('wiki_page_diff', kwargs={'slug': slug}),
                    urlencode(urldata)))
        form = WikiPageForm(data=request.POST or None, instance=wiki_page,
                initial={'content': content, 'summary': description})
    return render(request, 'mezawiki/wiki_page_edit.html', {'wiki_page': wiki_page, 'form': form})


def wiki_page_changes(request, 
                     template="mezawiki/wiki_page_changes.html"):
    """
    Displays a recent wiki changes.
    """
    wiki_pages = WikiPage.objects.published(for_user=request.user)
    wiki_revisions = WikiPageRevision.objects.filter(page__in=wiki_pages)
    context = {"wiki_revisions": wiki_revisions}
    return render(request, template, context)


def wiki_page_edit(request, slug, 
                     template="mezawiki/wiki_page_edit.html"):
    """
    Displays the form for editing a page.
    """
    try:
        #wiki_pages = WikiPage.objects.published(for_user=request.user)
        wiki_page = WikiPage.objects.get(slug=slug)
        wiki_page.is_initial = False
        initial = {}
    except WikiPage.DoesNotExist:
        wiki_page = WikiPage(slug=slug)
        wiki_page.is_initial = True
        initial = {'status': 1}

    if not wiki_page.can_edit_wikipage(request.user):
        return HttpResponseForbidden(
            _("You don't have permission to edit this wiki page."))

    if request.method == 'POST':
        form = WikiPageForm(request.POST, instance=wiki_page)
        if form.is_valid():
            page = form.save(commit=False)
            if wiki_page.is_initial:
                try:
                    page.user = request.user
                except:
                    page.user_id = -1
                page.title = deurlize_title(slug)
            page.save()
            if 'content' in form.changed_data:
                revision = WikiPageRevision()
                revision.content = page.content
                revision.description = form.cleaned_data["summary"]
                revision.page = page
                try:
                    revision.user = request.user
                except:
                    # anonymous
                    revision.user_id = -1
                revision.save()
            return HttpResponseRedirect(
                reverse('wiki_page_detail', args=[slug]))
    else:
        form = WikiPageForm(initial=initial, instance=wiki_page)

    context = {'wiki_page': wiki_page, 'form': form,
               'title': deurlize_title(slug)}
    return render(request, template, context)


def can_add_wikipage(user):
    # Simple cases first, we don't want to waste CPU and DB hits.

    # Everyone.
    if (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_OPENED):
        return True

    # Registered users.
    elif (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_REGISTERED
                                         ) and (isinstance(user, User)):
        return True

    # Moderated.
    elif (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_MODERATED
                   ) and (user.has_perm('mezzanine_wiki.add_wikipage')):
        return True

    # TODO closed.
    #elif (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_CLOSED):

    # Fallback to closed page.
    return False


def wiki_page_new(request, template="mezawiki/wiki_page_new.html"):
    """
    Displays the form for creating a page.
    """

    if not can_add_wikipage(request.user):
        return HttpResponseForbidden(
            _("You don't have permission to create wiki page."))

    if request.method == 'POST':
        form = WikiPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            try:
                page.user = request.user
            except:
                # anonymous
                page.user_id = -1
            page.slug = urlize_title(form.cleaned_data["title"])
            # TODO Check slug, it is not a unique field
            page.save()
            revision = WikiPageRevision()
            revision.content = page.content
            revision.description = form.cleaned_data["summary"]
            revision.page = page
            try:
                revision.user = request.user
            except:
                # anonymous
                revision.user_id = -1
            revision.save()
            return HttpResponseRedirect(
                reverse('wiki_page_detail', args=[page.slug]))
    else:
        form = WikiPageForm(initial={'status': 1})

    context = {'form': form}
    return render(request, template, context)


