try:
    from celery.task import PeriodicTask
    from celery.registry import tasks
except ImportError:
    PeriodicTask = object
    tasks = None

import logging
from datetime import timedelta

from . import settings as local_settings
from .models import Answer

logger = logging.getLogger('crowdsourcing.tasks')


class SyncFlickr(PeriodicTask):
    run_every = timedelta(minutes=5)

    def run(self, *args, **kwargs):
        logger.debug("Syncing flickr")
        Answer.sync_to_flickr()


if tasks and not local_settings.SYNCHRONOUS_FLICKR_UPLOAD:
    tasks.register(SyncFlickr)
