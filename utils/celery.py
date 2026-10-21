"""Celery base task that honours maintenance mode.

Wired in ``configurations/celery.py`` through ``task_cls``, so every task —
including the ``@shared_task`` ones in ``common/tasks.py`` — inherits it.
"""

import logging

from celery import Task

from utils import maintenance

logger = logging.getLogger(__name__)

# Deferrals are capped rather than unbounded: celery reads ``max_retries=None``
# as "use the task's own limit" (3 by default), which would drop tasks a few
# minutes into any maintenance window. At 30-600s per attempt this cap covers
# more than eight hours of downtime.
MAINTENANCE_MAX_RETRIES = 1000


class MaintenanceAwareTask(Task):
    """Defers execution while Celery is paused for maintenance.

    The check lives in ``before_start`` rather than in a ``task_prerun`` signal
    because celery only treats ``Retry`` as a reschedule inside the trace block
    that ``before_start`` runs in — raising it from the signal would simply fail
    the task instead of putting it back on the broker.

    Set ``maintenance_exempt = True`` on a task that must keep running.
    """

    maintenance_exempt = False

    def before_start(self, task_id, args, kwargs):
        if self.maintenance_exempt or not maintenance.is_celery_paused():
            return
        countdown = maintenance.get_retry_countdown()
        logger.info(
            "Celery is paused for maintenance, deferring task %s (%s) for %ss",
            self.name,
            task_id,
            countdown,
        )
        raise self.retry(countdown=countdown, max_retries=MAINTENANCE_MAX_RETRIES)

    def after_return(self, *args, **kwargs):
        # retry(max_retries=...) stores the limit on the task instance, which a
        # worker keeps around between executions. Drop it so a task's own
        # retries keep their own limit instead of inheriting the maintenance one.
        self.__dict__.pop("override_max_retries", None)
        super().after_return(*args, **kwargs)
