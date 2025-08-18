import logging
import os
import tempfile

from packtools import data_checker

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from config import celery_app
from core.utils.utils import _get_user

from .models import XMLDocument


User = get_user_model()


@celery_app.task(bind=True, name=_('Process XML Document'), timelimit=-1)
def task_process_xml_document(self, xml_id, user_id=None, username=None):
    user = _get_user(self.request, username=username, user_id=user_id)

    try:
        xml_document = XMLDocument.objects.get(id=xml_id)
    except XMLDocument.DoesNotExist:
        logging.error(f'XML document with ID {xml_id} does not exist.')
        return False
    
    logging.info(f'Processing XML file {xml_document.xml_file.name}.')
    task_validate_xml_file.delay(xml_id, user_id=user_id, username=username)
    task_generate_pdf_file.delay(xml_id, user_id=user_id, username=username)
    task_generate_html_file.delay(xml_id, user_id=user_id, username=username)
    
    return True
