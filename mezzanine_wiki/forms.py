from django import forms
from mezawiki.models import WikiPage


class PlainWidget(forms.Textarea):
    """
    A regular Textarea widget that is compatible with mezzanine richtext.
    """
    class Media:
        pass


class WikiPageForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = ('content',)
