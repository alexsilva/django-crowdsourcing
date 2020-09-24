import re

import django.forms
from django.apps import apps
from django.contrib.auth.models import ContentType
from django.core.files.images import get_image_dimensions
from django.forms import (
    BooleanField,
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    DateField,
    DateInput,
    EmailField,
    FloatField,
    Form,
    ImageField,
    IntegerField,
    MultipleChoiceField,
    RadioSelect,
    Textarea,
    ValidationError,
)
from django.forms.forms import BoundField
from django.forms.models import ModelForm
from django.template import Context, loader
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .fields import RankedChoiceField
from .geo import get_latitude_and_longitude
from .models import OPTION_TYPE_CHOICES, Answer, Submission
from .settings import VIDEO_URL_PATTERNS
from django.contrib.auth import get_user_model
from functools import reduce


User = get_user_model()

try:
    from crowdsourcing.oembedutils import oembed_expand
except ImportError:
    oembed_expand = None


class BaseAnswerForm(Form):
    def __init__(self,
                 question,
                 session_key,
                 submission=None,
                 *args,
                 **kwargs):
        self.question = question
        self.session_key = session_key
        self.submission = submission
        super(BaseAnswerForm, self).__init__(*args, **kwargs)
        self._configure_answer_field()

    def _configure_answer_field(self):
        answer = self.fields['answer']
        question = self.question
        answer.required = question.required
        answer.label = question.question
        answer.help_text = question.help_text
        # set some property on the basis of question.fieldname? TBD
        return answer

    def as_template(self):
        """Helper function for fieldsting fields data from form """
        bound_fields = [BoundField(self, field, name)
                        for name, field in self.fields.items()]
        c = Context(dict(form=self, bound_fields=bound_fields))
        t = loader.get_template('forms/form.html')
        return t.render(c)

    def save(self, commit=True):
        if self.cleaned_data['answer'] is None:
            if self.fields['answer'].required:
                raise ValidationError(_('This field is required.'))
            return
        ans = Answer()
        if self.submission:
            ans.submission = self.submission
        ans.question = self.question
        ans.value = self.cleaned_data['answer']
        if commit:
            ans.save()
        return ans


class TextInputAnswer(BaseAnswerForm):
    answer = CharField()


class IntegerInputAnswer(BaseAnswerForm):
    answer = IntegerField()


class FloatInputAnswer(BaseAnswerForm):
    answer = FloatField()


class BooleanInputAnswer(BaseAnswerForm):
    answer = BooleanField(initial=False)

    def clean_answer(self):
        value = self.cleaned_data['answer']
        if not value:
            return False
        return value

    def _configure_answer_field(self):
        fld = super(BooleanInputAnswer, self)._configure_answer_field()
        # we don't want to set this as required, as a single boolean field
        # being required doesn't make much sense in a survey
        fld.required = False
        return fld


class TextAreaAnswer(BaseAnswerForm):
    answer = CharField(widget=Textarea)


class DateAnswer(BaseAnswerForm):
    answer = DateField(widget=DateInput(attrs={'class': 'datepicker'}))


class EmailAnswer(BaseAnswerForm):
    answer = EmailField()


class VideoAnswer(BaseAnswerForm):
    answer = CharField()

    def clean_answer(self):
        value = self.cleaned_data['answer']
        if value:
            if oembed_expand:
                if oembed_expand(value):
                    return value
                else:
                    print("Couldn't expand {0}".format(value))
            else:
                matches = [re.match(v, value) for v in VIDEO_URL_PATTERNS]
                first_match = reduce(lambda x, y: x or y, matches)
                if first_match:
                    return first_match.group(0)
            raise ValidationError(_("Unknown video url format."))
        return value


class PhotoUpload(BaseAnswerForm):
    answer = ImageField()

    def clean_answer(self):
        answer = self.cleaned_data['answer']
        if answer and not get_image_dimensions(answer.file):
            raise ValidationError(_(
                "We couldn't read your file. Make sure it's a .jpeg, .png, or "
                ".gif file, not a .psd or other unsupported type."))
        return answer


class LocationAnswer(BaseAnswerForm):
    answer = CharField()

    def save(self, commit=True):
        obj = super(LocationAnswer, self).save(commit=False)
        if obj.value:
            obj.latitude, obj.longitude = get_latitude_and_longitude(obj.value)
            if commit:
                obj.save()
            return obj
        return None


class BaseOptionAnswer(BaseAnswerForm):
    def __init__(self, *args, **kwargs):
        super(BaseOptionAnswer, self).__init__(*args, **kwargs)
        options = self.question.parsed_options
        # appendChoiceButtons in survey.js duplicates this. jQuery and django
        # use " for html attributes, so " will mess them up.
        choices = []
        for x in options:
            choices.append(
                (strip_tags(x).replace('&amp;', '&').replace('"', "'").strip(),
                 mark_safe(x)))
        if not self.question.required and not isinstance(self, OptionCheckbox):
            choices = [('', '---------',)] + choices
        self.fields['answer'].choices = choices

    def clean_answer(self):
        key = self.cleaned_data['answer']
        if not key and self.fields['answer'].required:
            raise ValidationError(_('This field is required.'))
        if not isinstance(key, (list, tuple)):
            key = (key,)
        return key

    def save(self, commit=True):
        ans_list = []
        for text in self.cleaned_data['answer']:
            ans = Answer()
            if self.submission:
                ans.submission = self.submission
            ans.question = self.question
            ans.value = text
            if commit:
                ans.save()
            ans_list.append(ans)
        return ans_list


class OptionAnswer(BaseOptionAnswer):
    answer = ChoiceField()


class OptionRadio(BaseOptionAnswer):
    answer = ChoiceField(widget=RadioSelect)


class OptionCheckbox(BaseOptionAnswer):
    answer = MultipleChoiceField(widget=CheckboxSelectMultiple)


class RankedAnswer(BaseOptionAnswer):
    answer = RankedChoiceField()


# Each question gets a form with one element determined by the type for the
# answer.
QTYPE_FORM = {
    OPTION_TYPE_CHOICES.CHAR: TextInputAnswer,
    OPTION_TYPE_CHOICES.INTEGER: IntegerInputAnswer,
    OPTION_TYPE_CHOICES.FLOAT: FloatInputAnswer,
    OPTION_TYPE_CHOICES.BOOL: BooleanInputAnswer,
    OPTION_TYPE_CHOICES.TEXT: TextAreaAnswer,
    OPTION_TYPE_CHOICES.DATE: DateAnswer,
    OPTION_TYPE_CHOICES.SELECT: OptionAnswer,
    OPTION_TYPE_CHOICES.CHOICE: OptionRadio,
    OPTION_TYPE_CHOICES.NUMERIC_SELECT: OptionAnswer,
    OPTION_TYPE_CHOICES.NUMERIC_CHOICE: OptionRadio,
    OPTION_TYPE_CHOICES.BOOL_LIST: OptionCheckbox,
    OPTION_TYPE_CHOICES.EMAIL: EmailAnswer,
    OPTION_TYPE_CHOICES.PHOTO: PhotoUpload,
    OPTION_TYPE_CHOICES.VIDEO: VideoAnswer,
    OPTION_TYPE_CHOICES.LOCATION: LocationAnswer,
    OPTION_TYPE_CHOICES.RANKED: RankedAnswer,
}


class SubmissionForm(ModelForm):
    """SubmissionForm"""

    def __init__(self, survey, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)
        self.survey = survey

    class Meta:
        model = Submission
        exclude = (
            'survey',
            'submitted_at',
            'ip_address',
            'user',
            'is_public',
            'featured')


class SurveyFormFilter(django.forms.Form):
    content_type = django.forms.CharField(label="content-type",
                                          widget=django.forms.HiddenInput,
                                          required=False)

    object_pk = django.forms.IntegerField(label="object-pk",
                                          widget=django.forms.HiddenInput,
                                          required=False)

    creator = django.forms.IntegerField(label="creator", required=False)
    is_published = django.forms.BooleanField(label='is published',
                                             required=False,
                                             initial=True)
    request_filter = ('creator', 'is_published')

    @classmethod
    def get_field_filters(cls, params):
        filters = {}
        for field_name in cls.request_filter:
            value = params.pop(field_name, cls.base_fields[field_name].initial)
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            filters[field_name] = value
        return filters

    def clean_content_type(self):
        content_type = self.cleaned_data.get('content_type')
        if not content_type:
            return content_type
        try:
            app_label, model_name = content_type.split('.')
        except ValueError:
            raise ValidationError(_("invalid format 'app_label.model_name'"))
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise ValidationError(_("invalid 'app_label'"))
        return ContentType.objects.get_for_model(model)

    def clean_object_pk(self):
        object_pk = self.cleaned_data.get('object_pk')
        content_type = self.cleaned_data.get('content_type')
        content_type_instance = isinstance(content_type, ContentType)
        if object_pk:
            if not content_type_instance:
                raise ValidationError(_("broken relation"))
            model = apps.get_model(content_type.app_label, content_type.model)
            try:
                model.objects.get(pk=object_pk)
            except model.DoesNotExist:
                raise ValidationError(_("invalid object pk"))
        elif content_type_instance:
            raise ValidationError(_("broken relation"))
        return object_pk

    def clean_creator(self):
        """The user who creates the survey"""
        creator = self.cleaned_data['creator']
        if not creator:
            return None
        try:
            creator = User.objects.get(pk=creator)
        except User.DoesNotExist:
            raise ValidationError(_("invalid user pk"))
        return creator

    @property
    def filter_kwargs(self):
        kwargs = self.cleaned_data.copy()
        related_prefix = 'content__'
        kwargs[related_prefix + 'content_type'] = kwargs.pop('content_type')
        kwargs[related_prefix + 'object_pk'] = kwargs.pop('object_pk')
        return kwargs


class SubmissionFormFilter(SurveyFormFilter):
    """Form used as the filter base for submissions related to a survey content"""

    @property
    def filter_kwargs(self):
        kwargs = self.cleaned_data.copy()
        related_prefix = 'survey__'
        filter_kwargs = {
            related_prefix + 'content__content_type': kwargs.pop('content_type'),
            related_prefix + 'content__object_pk': kwargs.pop('object_pk')
        }
        for field_name in kwargs:
            filter_kwargs[related_prefix + field_name] = kwargs.get(field_name)
        return filter_kwargs


def forms_for_survey(survey, request='testing', submission=None):
    testing = bool(request == 'testing')
    session_key = "" if testing or not request.user.is_authenticated else request.session.session_key.lower()
    post = None if testing else request.POST or None
    files = None if testing else request.FILES or None
    main_form = SubmissionForm(survey, data=post, files=files)
    forms = [main_form]
    for q in survey.questions.all().order_by("order"):
        forms.append(_form_for_question(q, session_key, submission, post, files))
    return forms


def _form_for_question(question,
                       session_key="",
                       submission=None,
                       data=None,
                       files=None):
    return QTYPE_FORM[question.option_type](
        question=question,
        session_key=session_key,
        submission=submission,
        prefix='%s_%s' % (question.survey.id, question.id),
        data=data,
        files=files)
