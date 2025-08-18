from django.db import models
from django.utils.translation import gettext_lazy as _


class XMLDocument(models.Model):
    xml_file = models.FileField(
        upload_to='xml_manager/xml/',
        verbose_name=_("XML File"),
        help_text=_("Upload an XML file for processing.")
    )
    validation_file = models.FileField(
        upload_to='xml_manager/csv/',
        blank=True,
        null=True,
        verbose_name=_("Validation File")
    )
    exceptions_file = models.FileField(
        upload_to='xml_manager/exceptions/',
        blank=True,
        null=True,
        verbose_name=_("Exceptions File")
    )
    pdf_file = models.FileField(
        upload_to='xml_manager/pdf/',
        blank=True,
        null=True,
        verbose_name=_("PDF File")
    )
    html_file = models.FileField(
        upload_to='xml_manager/html/',
        blank=True,
        null=True,
        verbose_name=_("HTML File")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded At"),
        help_text=_("The date and time when the file was uploaded.")
    )
