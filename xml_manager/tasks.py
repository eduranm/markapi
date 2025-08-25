import logging
import os
import tempfile

from packtools import data_checker
from packtools.sps.formats.pdf.pipeline import docx
from packtools.sps.formats.pdf.utils import file_utils
from packtools.sps.utils import xml_utils
from django.core.files import File
from django.conf import settings

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from config import celery_app
from tracker.choices import (
    XML_DOCUMENT_PARSING_ERROR,
    XML_DOCUMENT_VALIDATION_ERROR,
    XML_DOCUMENT_CONVERSION_TO_DOCX_ERROR,
    XML_DOCUMENT_CONVERSION_TO_PDF_ERROR,
    XML_DOCUMENT_CONVERSION_TO_TEX_ERROR,
)
from tracker.models import XMLDocumentEvent

from .models import (
    XMLDocument, 
    XMLDocumentHTML, 
    XMLDocumentPDF,
)


User = get_user_model()


def _get_user(request, username=None, user_id=None):
    try:
        return User.objects.get(pk=request.user_id)
    except AttributeError:
        if user_id:
            return User.objects.get(pk=user_id)
        if username:
            return User.objects.get(username=username)


@celery_app.task(bind=True, timelimit=-1)
def task_process_xml_document(self, xml_id, user_id=None, username=None):
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


@celery_app.task(bind=True, timelimit=-1)
def task_validate_xml_file(self, xml_id, user_id=None, username=None):
    try:
        xml_document = XMLDocument.objects.get(id=xml_id)
    except XMLDocument.DoesNotExist:
        logging.error(f'XML file with ID {xml_id} does not exist.')
        return False
    
    user = _get_user(self.request, username=username, user_id=user_id)
    
    logging.info(f'Starting XML validation for XML file {xml_document.xml_file.name}.')
    params = {}

    base_filename = os.path.splitext(os.path.basename(xml_document.xml_file.name))[0]

    validation_dir = os.path.join(settings.MEDIA_ROOT, 'xml_manager', 'validation')
    exceptions_dir = os.path.join(settings.MEDIA_ROOT, 'xml_manager', 'validation')
    os.makedirs(validation_dir, exist_ok=True)
    os.makedirs(exceptions_dir, exist_ok=True)

    path_csv = os.path.join(validation_dir, f"{base_filename}.validation.csv")
    path_exceptions = os.path.join(exceptions_dir, f"{base_filename}.exceptions.json")

    try:
        validator = data_checker.XMLDataChecker(path_csv, path_exceptions, xml_document.xml_file.path)
        validator.validate(params=params, csv_per_xml=False)
    except Exception as e:
        logging.error(f'Error during XML validation: {e}')
        XMLDocumentEvent.create(
            xml_document=xml_document,
            error_type=XML_DOCUMENT_VALIDATION_ERROR,
            data={},
            message=str(e),
            save=True,
        )
        return False
    
    with open(path_csv, 'rb') as f_csv:
        xml_document.validation_file.save(os.path.basename(path_csv), File(f_csv), save=False)

    with open(path_exceptions, 'rb') as f_exc:
        xml_document.exceptions_file.save(os.path.basename(path_exceptions), File(f_exc), save=False)

    xml_document.save()
    logging.info(f'XML validation completed successfully for {xml_document.xml_file.name}.')
    return True


@celery_app.task(bind=True, timelimit=-1)
def task_generate_pdf_file(self, xml_id, user_id=None, username=None):    
    try:
        xml_document = XMLDocument.objects.get(id=xml_id)
    except XMLDocument.DoesNotExist:
        logging.error(f'XML file with ID {xml_id} does not exist.')
        return False
    
    user = _get_user(self.request, username=username, user_id=user_id)

    try:
        xml_tree = xml_utils.get_xml_tree(xml_document.xml_file.path)
    except Exception as e:
        logging.error(f'Error parsing XML file: {e}')
        XMLDocumentEvent.create(
            xml_document=xml_document,
            error_type=XML_DOCUMENT_PARSING_ERROR,
            data={},
            message=str(e),
            save=True,
        )
        return False

    # TODO: Iterate over available languages

    logging.info(f'Starting PDF generation for XML file {xml_document.xml_file.name}.')
    try:
        base_docx_layout = os.path.join(settings.MEDIA_ROOT, 'layout.docx')
        document = docx.pipeline_docx(xml_tree, data={'base_layout': base_docx_layout})
    except Exception as e:
        logging.error(f'Error during PDF generation: {e}')
        XMLDocumentEvent.create(
            xml_document=xml_document,
            error_type=XML_DOCUMENT_CONVERSION_TO_DOCX_ERROR,
            data={},
            message=str(e),
            save=True,
        )
        return False

    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'xml_manager', 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)

    # DOCX intermediário
    temp_dir = tempfile.gettempdir()
    base_filename = os.path.splitext(os.path.basename(xml_document.xml_file.name))[0]
    path_intermediate_docx = os.path.join(temp_dir, f"{base_filename}.docx")
    document.save(path_intermediate_docx)

    path_pdf = os.path.join(pdf_dir, f"{base_filename}.pdf")
    try:
        file_utils.convert_docx_to_pdf(path_intermediate_docx, path_pdf)
    except Exception as e:
        logging.error(f'Error during DOCX to PDF conversion: {e}')
        XMLDocumentEvent.create(
            xml_document=xml_document,
            error_type=XML_DOCUMENT_CONVERSION_TO_PDF_ERROR,
            data={},
            message=str(e),
            save=True,
        )
        return False

    with open(path_pdf, 'rb') as f_pdf:
        pdf_instance = XMLDocumentPDF(xml_document=xml_document, language="pt")
        pdf_instance.pdf_file.save(os.path.basename(path_pdf), File(f_pdf), save=True)

    return True


@celery_app.task(bind=True, timelimit=-1)
def task_generate_html_file(self, xml_id, user_id=None, username=None):    
    try:
        xml_file = XMLDocument.objects.get(id=xml_id)
    except XMLDocument.DoesNotExist:
        logging.error(f'XML file with ID {xml_id} does not exist.')
        return False
    
    user = _get_user(self.request, username=username, user_id=user_id)
    
    logging.info(f'Starting HTML generation for XML file {xml_file.xml_file.name}.')
    # TODO: Implement HTML generation logic here
