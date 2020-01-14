from django import forms
from django.template.loader import render_to_string


class RankedChoiceWidget(forms.MultiWidget):
    """ A widget which displays n select boxes, recording
        ranked choices from 1-n.
    """

    def __init__(self, attrs=None, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        _widgets = (
            forms.Select(attrs=attrs, choices=choices),
            forms.Select(attrs=attrs, choices=choices),
            forms.Select(attrs=attrs, choices=choices),
        )
        super(RankedChoiceWidget, self).__init__(_widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            val = value.split(',')
            return [val[0], val[1], val[2]]
        return [None, None, None]

    def format_output(self, rendered_widgets):
        markup = render_to_string(
            'crowdsourcing/forms/widgets/ranked_choice.html',
            context={'rendered_widgets': rendered_widgets}
        )
        return markup
