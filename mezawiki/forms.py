from django import forms

class PlainWidget(forms.Textarea):
    """
    A regular Textarea widget that is compatible with mezzanine richtext.
    """

    class Media:
        pass
