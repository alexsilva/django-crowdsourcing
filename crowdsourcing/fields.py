from __future__ import absolute_import

import copy

from django.db.models.fields.files import ImageFieldFile
from django.forms import MultiValueField
from django.forms.fields import ChoiceField

from .widgets import RankedChoiceWidget
try:
    from sorl.thumbnail.fields import ImageField
except ImportError:
    from django.db.models import ImageField


class ImageFieldThumbnailsFile(ImageFieldFile):

    @property
    def extra_thumbnails(self):
        return self.field.extra_thumbnails

    @property
    def thumbnail_tag(self):
        return self.name

    @property
    def thumbnail(self):
        from sorl.thumbnail import get_thumbnail
        size = self.extra_thumbnails['default']['size']
        return get_thumbnail(self.file, "x".join([str(s) for s in size]))


class ImageWithThumbnailsField(ImageField):
    attr_class = ImageFieldThumbnailsFile

    def __init__(self, *args, **kwargs):
        self.extra_thumbnails = kwargs.pop('extra_thumbnails', None)
        super(ImageWithThumbnailsField, self).__init__(*args, **kwargs)


class RankedChoiceField(MultiValueField):
    widget = RankedChoiceWidget

    def __init__(self, choices=None, *args, **kwargs):
        if choices is None:
            choices = ()

        fields = (
            ChoiceField(),
            ChoiceField(),
            ChoiceField(),
        )
        super(RankedChoiceField, self).__init__(fields, *args, **kwargs)
        self.choices = choices

    def __deepcopy__(self, memo):
        result = super(RankedChoiceField, self).__deepcopy__(memo)
        result.fields = copy.deepcopy(self.fields, memo)
        return result

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)

    def _set_choices(self, value):
        self._choices = list(value)

        # set on field for validation
        for field in self.fields:
            field.choices = self._choices

        # set on widget for rendering
        for widget in self.widget.widgets:
            widget.choices = self._choices

    def _get_choices(self):
        return self._choices

    choices = property(_get_choices, _set_choices)
