from django.db.models import Manager, Q, CharField, TextField, get_models
from mezzanine.conf import settings
from mezzanine.core.managers import CurrentSiteManager, SearchableManager


class PublishedManager(Manager):
    """
    Provides filter for restricting items returned by status and
    publish date when the given user is not a staff member.
    """

    def published(self, for_user=None):
        """
        For non-staff users, return items with a published status and
        whose publish and expiry dates fall before and after the
        current date when specified.
        """
        from mezzanine.core.models import CONTENT_STATUS_PUBLISHED, CONTENT_STATUS_DRAFT
        if for_user is not None and for_user.is_staff:
            return self.all()
        if for_user is not None and for_user.has_perm('mezzanine_wiki.view_wikipage'):
            status_filter = Q(status=CONTENT_STATUS_PUBLISHED) | Q(status=CONTENT_STATUS_DRAFT)
        else:
            status_filter = Q(status=CONTENT_STATUS_PUBLISHED)
        return self.filter(
            Q(publish_date__lte=now()) | Q(publish_date__isnull=True),
            Q(expiry_date__gte=now()) | Q(expiry_date__isnull=True),
            status_filter)

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class DisplayableManager(CurrentSiteManager, PublishedManager,
                         SearchableManager):
    """
    Manually combines ``CurrentSiteManager``, ``PublishedManager``
    and ``SearchableManager`` for the ``Displayable`` model.

    """
    pass
