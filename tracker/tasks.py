from datetime import datetime

from config import celery_app
from .models import GeneralEvent


@celery_app.task(bind=True)
def delete_general_events(self, exception_type, start_date=None, end_date=None, user_id=None, username=None):
    """
    Delete GeneralEvent records based on exception type and optional date range.
    """

    filters = {}
    if exception_type:
        filters['exception_type__icontains'] =  exception_type

    if start_date:
        start_date = datetime.fromisoformat(start_date)
        filters['created__gte'] = start_date
    if end_date:
        end_date = datetime.fromisoformat(end_date)
        filters['created__lte'] = end_date

    GeneralEvent.objects.filter(**filters).delete()
