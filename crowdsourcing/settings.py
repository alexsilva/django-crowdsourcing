from django.conf import settings

# there are several admin apps for django.
CROWDSOURCING_ADMIN_APP_NAME = getattr(settings, "CROWDSOURCING_APP_NAME", "admin")

CROWDSOURCING_APP_NAME = getattr(settings, "CROWDSOURCING_APP_NAME", "Survey")

# This sets the default "Moderate submissions" value of surveys.
MODERATE_SUBMISSIONS = getattr(settings,
                               'CROWDSOURCING_MODERATE_SUBMISSIONS',
                               False)

IMAGE_UPLOAD_PATTERN = getattr(settings,
                               'CROWDSOURCING_IMAGE_UPLOAD_PATTERN',
                               'crowdsourcing/images/%Y/%m/%d')

# You can set a function that does additional processing on the submission
# list before rendering. For example, if your user interface has sorting
# based on votes, you could set this value. Use a python path to a function
# that takes a submission list and a request object.
PRE_REPORT = getattr(settings, 'CROWDSOURCING_PRE_REPORT', '')

# If a survey is set to e-mail someone every time someone enters the survey,
# this will be the return address.
SURVEY_EMAIL_FROM = getattr(settings, 'CROWDSOURCING_SURVEY_EMAIL_FROM', None)
if SURVEY_EMAIL_FROM is None:
    SURVEY_EMAIL_FROM = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
if SURVEY_EMAIL_FROM is None:
    SURVEY_EMAIL_FROM = 'donotreply@donotreply.com'

# This site is for the notification emails that crowdsourcing sends when
# a user enters a survey. The default is the site the user entered the survey
# on.
SURVEY_ADMIN_SITE = getattr(settings, 'CROWDSOURCING_SURVEY_ADMIN_SITE', '')

# You can set a custom def oembed_expand(url, **opts) which takes the url to
# a video and returns html embed code. Use the form path.to.my_function
OEMBED_EXPAND = getattr(settings, 'CROWDSOURCING_OEMBED_EXPAND', '')

# What URL should crowdsourcing redirect users to if they try to enter a survey
# that requires a login?
LOGIN_VIEW = getattr(settings, 'CROWDSOURCING_LOGIN_VIEW', '')

# youtube has a lot of characters in their ids now so use [^&]
# youtube also likes to add additional query arguments, so no trailing $
# If you have oembed installed, crowdsourcing uses the oembed configuration and
# ignores this.
VIDEO_URL_PATTERNS = getattr(
    settings,
    'CROWDSOURCING_VIDEO_URL_PATTERNS',
    (r'^http://www\.youtube\.com/watch\?v=[^&]+',))

# crowdsourcing.templatetags.crowdsourcing.google_map uses this setting.
GOOGLE_MAPS_API_KEY = getattr(settings, 'CROWDSOURCING_GOOGLE_MAPS_API_KEY', '')

# A dictionary of extra thumbnails for Submission.image_answer, which is a sorl
# ImageWithThumbnailsField. For example, {'slideshow': {'size': (620, 350)}}
# max_enlarge is in case users upload huge images that enlarge far too big.
EXTRA_THUMBNAILS = {
    'default': {'size': (250, 250)},
    'max_enlarge': {'size': (1000, 1000)}
}
EXTRA_THUMBNAILS.update(getattr(settings, 'CROWDSOURCING_EXTRA_THUMBNAILS', {}))
