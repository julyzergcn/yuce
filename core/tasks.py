from django.utils import timezone
from celery import task

from core.util import *
from core.models import *


@task
def mark_available_deadline():
    for topic in Topic.objects.filter(status='open', deadline__lte=timezone.now()):
        mark_deadline.delay(topic)

@task
def mark_available_event_closed():
    for topic in Topic.objects.filter(status__in=('open', 'deadline'), event_close_date__lte=timezone.now()):
        mark_event_closed.delay(topic)
