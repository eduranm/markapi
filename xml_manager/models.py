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
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded At"),
        help_text=_("The date and time when the file was uploaded.")
    )


class XMLDocumentPDF(models.Model):
    xml_document = models.ForeignKey(XMLDocument, on_delete=models.CASCADE, related_name="pdfs", verbose_name=_("XML Document"))
    pdf_file = models.FileField(
        upload_to='xml_manager/pdf/',
        verbose_name=_("PDF File")
    )
    language = models.CharField(
        max_length=32,
        default="pt",
        verbose_name=_("Language"),
        help_text=_("Language code or name")
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))


class XMLDocumentHTML(models.Model):
    xml_document = models.ForeignKey(XMLDocument, on_delete=models.CASCADE, related_name="htmls", verbose_name=_("XML Document"))
    html_file = models.FileField(
        upload_to='xml_manager/html/',
        verbose_name=_("HTML File")
    )
    language = models.CharField(
        max_length=32,
        default="pt",
        verbose_name=_("Language"),
        help_text=_("Language code or name")
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
