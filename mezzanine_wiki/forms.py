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
    description = forms.CharField(label=_("Description"),
                                  max_length=400, required=False)

    class Meta:
        model = WikiPage
        fields = ('content', 'privacy',)

    def __init__(self, *args, **kwargs):
        super(WikiPageForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'


class WikiPagePublicForm(forms.ModelForm):
    description = forms.CharField(label=_("Description"),
                                  max_length=400, required=False)

    class Meta:
        model = WikiPage
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(WikiPagePublicForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'


class WikiPageNewForm(forms.ModelForm):
    description = forms.CharField(label=_("Description"),
                                  max_length=400, required=False)

    class Meta:
        model = WikiPage
        fields = ('title', 'content',)

    def __init__(self, *args, **kwargs):
        super(WikiPageNewForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['class'] = 'wiki-textarea'

