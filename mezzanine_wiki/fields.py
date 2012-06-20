from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.utils.importing import import_dotted_path


class WikiTextField(models.TextField):
    """
    TextField that stores markup text.
    """

    def formfield(self, **kwargs):
        """
        Apply the widget class defined by the
        ``WIKI_TEXT_WIDGET_CLASS`` setting.
        """
        from mezzanine.conf import settings
        try:
            widget_class = import_dotted_path(settings.WIKI_TEXT_WIDGET_CLASS)
        except ImportError:
            raise ImproperlyConfigured(_("Could not import the value of "
                                         "settings.WIKI_TEXT_WIDGET_CLASS: %s"
                                         % settings.WIKI_TEXT_WIDGET_CLASS))
        kwargs["widget"] = widget_class()
        formfield = super(WikiTextField, self).formfield(**kwargs)
        return formfield


# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules(rules=[((WikiTextField,), [], {})],
            patterns=["mezzanine_wiki\.fields\."])
    except ImportError:
        pass
