# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged, TimeStamped
from mezzanine.generic.fields import CommentsField, RatingField
from mezzanine_wiki.fields import WikiTextField
from mezzanine_wiki import defaults as wiki_settings
from django.utils.timezone import now
from mezzanine_wiki.managers import DisplayableManager


WIKIPAGE_PERMISSIONS = (
    ('view_wikipage', 'Can view wikipage'),
    ('change_wikipage_privacy', 'Can change wikipage privacy'),
)

WIKIPAGE_REVISION_PERMISSIONS = (
    ('view_wikipage_revision', 'Can view wikipage revision'),
)


class WikiPage(Displayable, Ownable):
    """
    A wiki page.
    """

    content = WikiTextField(_("Content"))
    categories = models.ManyToManyField("WikiCategory",
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="wikipages")
    allow_comments = models.BooleanField(verbose_name=_("Allow comments"),
                                         default=True)
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"), null=True,
                               upload_to="wiki", max_length=255, blank=True)

    search_fields = ("content",)

    objects = DisplayableManager()

    class Meta:
        verbose_name = _("Wiki page")
        verbose_name_plural = _("Wiki pages")
        ordering = ("title",)
        permissions = WIKIPAGE_PERMISSIONS

    def can_view_wikipage(self, user):
        # Everyone.
        return True

    def can_edit_wikipage(self, user):
        # Simple cases first, we don't want to waste CPU and DB hits.

        # Everyone.
        if (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_OPENED):
            return True

        # Registered users.
        elif (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_REGISTERED
                                              ) and (user.is_authenticated()):
            return True

        # TODO: Checks done by guardian for owner and admins.
        #elif 'view_wikipage' in get_perms(user, self):
        elif (settings.WIKI_PRIVACY == wiki_settings.WIKI_PRIVACY_MODERATED
                   ) and (user.has_perm('mezzanine_wiki.change_wikipage')):
            return True

        # Owner.
        elif self.user == user:
            return True

        # Fallback to closed page.
        return False

    def get_absolute_url(self):
        return reverse("wiki_page_detail", kwargs={"slug": self.slug})


class WikiPageRevision(Ownable, TimeStamped):
    """
    A wiki page revision.
    """

    page = models.ForeignKey("WikiPage", verbose_name=_("Wiki page"))
    content = WikiTextField(_("Content"))
    description = models.CharField(_("Description"),
                                   max_length=400, blank=True)

    class Meta:
        verbose_name = _("Wiki page revision")
        verbose_name_plural = _("Wiki page revisions")
        ordering = ("-created",)
        permissions = WIKIPAGE_REVISION_PERMISSIONS

    def __unicode__(self):
        return "%s" % self.created

    def get_absolute_url(self):
        return reverse("wiki_page_revision", kwargs={"slug": self.page.slug,
                                                     "rev_id": self.id})


class WikiCategory(Slugged):
    """
    A category for grouping wiki pages.
    """

    class Meta:
        verbose_name = _("Wiki Category")
        verbose_name_plural = _("Wiki Categories")

    def get_absolute_url(self):
        return reverse("wiki_page_list_category", kwargs={"slug": self.slug})
