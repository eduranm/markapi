from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


class XMLDocument(models.Model):
    xml_file = models.FileField(
        upload_to='xml_manager/xml/',
        verbose_name=_("XML File"),
        help_text=_("Upload an XML file for processing.")
    )
    validation_file = models.FileField(
        upload_to='xml_manager/validation/',
        blank=True,
        null=True,
        verbose_name=_("Validation File")
    )
    exceptions_file = models.FileField(
        upload_to='xml_manager/validation/',
        blank=True,
        null=True,
        verbose_name=_("Exceptions File")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded At"),
        help_text=_("The date and time when the file was uploaded.")
    )

    panels = [
        FieldPanel("xml_file"),
    ]

    def __str__(self):
        return f"{self.xml_file.name}"
        
    class Meta:
        verbose_name = _("XML Document")
        verbose_name_plural = _("XML Documents")


class XMLDocumentPDF(models.Model):
    xml_document = models.ForeignKey(XMLDocument, on_delete=models.CASCADE, related_name="pdfs", verbose_name=_("XML Document"))
    pdf_file = models.FileField(
        upload_to='xml_manager/pdf/',
        verbose_name=_("PDF File")
    )
    docx_file = models.FileField(
        upload_to='xml_manager/docx/',
        verbose_name=_("DOCX File"),
        null=True,
        blank=True,
        help_text=_('Intermediate DOCX file generated during PDF creation')
    )
    language = models.CharField(
        max_length=32,
        default="pt",
        verbose_name=_("Language"),
        help_text=_("Language code or name")
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))

    def __str__(self):
        return f"PDF for {self.xml_document.xml_file.name} ({self.language})"
    
    class Meta:
        verbose_name = _("XML Document PDF")
        verbose_name_plural = _("XML Document PDFs")

    @classmethod
    def create(cls, xml_document, pdf_file, language="pt"):
        pdf_instance = cls(
            xml_document=xml_document, 
            pdf_file=pdf_file, 
            language=language
        )
        pdf_instance.save()
        return pdf_instance


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

    def __str__(self):
        return f"HTML for {self.xml_document.xml_file.name} ({self.language})"
    
    class Meta:
        verbose_name = _("XML Document HTML")
        verbose_name_plural = _("XML Document HTMLs")

    @classmethod
    def create(cls, xml_document, html_file, language="pt"):
        html_instance = cls(
            xml_document=xml_document, 
            html_file=html_file, 
            language=language
        )
        html_instance.save()
        return html_instance
