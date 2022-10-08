from django.shortcuts import render
from django.template import RequestContext

from crowdsourcing.models import Survey


def home(request):
    latest_survey = None
    surveys = Survey.live.order_by('-survey_date')
    if surveys:
        latest_survey = surveys[0]
    context = RequestContext(request)
    context.update({
        "latest_survey": latest_survey
    })
    return render(request, "home.html", context)
