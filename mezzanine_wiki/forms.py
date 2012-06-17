from django import forms
from mezzanine_wiki.models import WikiPage


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

    def __init__(self, *args, **kwargs):
        super(WikiPageForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'

