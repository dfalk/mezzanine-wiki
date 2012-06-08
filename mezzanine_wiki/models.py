
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.generic.fields import CommentsField, RatingField
from mezzanine_wiki.fields import WikiTextField


class WikiText(models.Model):
    """
    Provides a Markup Text field for managing general content and making
    it searchable.
    """

    content = WikiTextField(_("Content"))

    search_fields = ("content",)

    class Meta:
        abstract = True


class WikiPage(Displayable, Ownable, WikiText):
    """
    A wiki page.
    """

    categories = models.ManyToManyField("WikiCategory",
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="wikipages")
    allow_comments = models.BooleanField(verbose_name=_("Allow comments"),
                                         default=True)
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"), null=True,
                               upload_to="wiki", max_length=255, blank=True)

    class Meta:
        verbose_name = _("Wiki page")
        verbose_name_plural = _("Wiki pages")
        ordering = ("title",)

    @models.permalink
    def get_absolute_url(self):
        url_name = "wiki_page_detail"
        kwargs = {"slug": self.slug}
        return (url_name, (), kwargs)


class WikiCategory(Slugged):
    """
    A category for grouping wiki pages.
    """

    class Meta:
        verbose_name = _("Wiki Category")
        verbose_name_plural = _("Wiki Categories")

    @models.permalink
    def get_absolute_url(self):
        return ("wiki_page_list_category", (), {"slug": self.slug})
