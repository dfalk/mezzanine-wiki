from django import forms
from django.utils.translation import ugettext_lazy as _
from mezzanine_wiki.models import WikiPage


class PlainWidget(forms.Textarea):
    """
    A regular Textarea widget that is compatible with mezzanine richtext.
    """
    class Media:
        pass


class WikiPageForm(forms.ModelForm):
    summary = forms.CharField(label=_("Edit summary"),
                                  max_length=400, required=False)

    class Meta:
        model = WikiPage
        fields = ('status', 'content', 'summary',)

    def __init__(self, *args, **kwargs):
        super(WikiPageForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'


class WikiPageNewForm(forms.ModelForm):
    summary = forms.CharField(label=_("Edit summary"),
                                  max_length=400, required=False)

    class Meta:
        model = WikiPage
        fields = ('status', 'title', 'content', 'summary')

    def __init__(self, *args, **kwargs):
        super(WikiPageNewForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'

