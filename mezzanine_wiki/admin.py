from copy import deepcopy
from django.contrib import admin

from mezzanine.conf import settings
from mezzanine.core.admin import StackedDynamicInlineAdmin
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin

from mezzanine_wiki.models import WikiPage, WikiPageRevision, WikiCategory


wikipage_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
wikipage_fieldsets[0][1]["fields"].insert(1, "categories")
wikipage_fieldsets[0][1]["fields"].append("content")
wikipage_fieldsets[0][1]["fields"].append("allow_comments")
if settings.WIKI_USE_FEATURED_IMAGE:
    wikipage_fieldsets[0][1]["fields"].insert(-2, "featured_image")


class WikiPageRevisionInline(StackedDynamicInlineAdmin):
    model = WikiPageRevision
    extra = 0


class WikiPageAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for wiki pages.
    """

    fieldsets = wikipage_fieldsets
    list_display = ("title", "user", "status", "admin_link")
    filter_horizontal = ("categories",)
    inlines = (WikiPageRevisionInline,)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class WikiCategoryAdmin(admin.ModelAdmin):
    """
    Admin class for wiki categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "mezawiki.WikiCategory" in items:
                return True
        return False


admin.site.register(WikiPage, WikiPageAdmin)
admin.site.register(WikiCategory, WikiCategoryAdmin)
