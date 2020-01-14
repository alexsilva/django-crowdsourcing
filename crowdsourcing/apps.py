from django.apps import AppConfig

from crowdsourcing.settings import CROWDSOURCING_APP_NAME


class CrowdsourcingAppConfig(AppConfig):
    name = 'crowdsourcing'
    verbose_name = CROWDSOURCING_APP_NAME
