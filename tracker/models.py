import json
import logging
import traceback
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import CommonControlField
from xml_manager.models import XMLDocument
from tracker import choices

from .exceptions import (
    GeneralEventCreateError,
    XMLDocumentEventCreateError,
)


class XMLDocumentEvent(CommonControlField):
    xml_document = models.ForeignKey(
        XMLDocument, 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False,
        db_index=True,
    )
    error_type = models.CharField(
        _("Error Type"),
        choices=choices.XML_DOCUMENT_EVENT,
        max_length=3,
        null=True,
        blank=True,
    )
    data = models.JSONField(
        _("Data"),
        default=dict,
    )
    message = models.TextField(
        _("Message"),
        null=True,
        blank=True,
    )
    handled = models.BooleanField(
        _("Handled"),
        default=False
    )

    @classmethod
    def create(cls, xml_document, error_type, data, message, save=False):
        try:
            obj = cls()
            obj.xml_document = xml_document
            obj.error_type = error_type
            obj.data = data
            obj.message = message
            if save:
                obj.save()

            return obj

        except Exception as exc:
            raise XMLDocumentEventCreateError(
                f"Unable to create XMLDocumentEvent. EXCEPTION {exc}"
            )

    def __str__(self):
        return f"{self.data} - {self.message}"
    
    class Meta:
        verbose_name = _("XML Document Event")
        verbose_name_plural = _("XML Document Events")


class GeneralEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(verbose_name=_("Creation date"), auto_now_add=True)
    exception_type = models.TextField(_("Exception Type"), null=True, blank=True)
    exception_msg = models.TextField(_("Exception Msg"), null=True, blank=True)
    traceback = models.JSONField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)
    item = models.CharField(
        _("Item"),
        max_length=256,
        null=True,
        blank=True,
    )
    action = models.CharField(
        _("Action"),
        max_length=256,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["exception_type"]),
            models.Index(fields=["item"]),
            models.Index(fields=["action"]),
        ]
        ordering = ["-created"]
        verbose_name = _("General Event")
        verbose_name_plural = _("General Events")

    def __str__(self):
        if self.item or self.action:
            return f"{self.action} {self.item} {self.exception_msg}"
        return f"{self.exception_msg}"

    @property
    def data(self):
        return dict(
            created=self.created.isoformat(),
            item=self.item,
            action=self.action,
            exception_type=self.exception_type,
            exception_msg=self.exception_msg,
            traceback=json.dumps(self.traceback),
            detail=json.dumps(self.detail),
        )

    @classmethod
    def create(
        cls,
        exception=None,
        exc_traceback=None,
        item=None,
        action=None,
        detail=None,
    ):
        try:
            if exception:
                logging.exception(exception)

            obj = cls()
            obj.item = item
            obj.action = action
            obj.exception_msg = str(exception)
            obj.exception_type = str(type(exception))
            try:
                json.dumps(detail)
                obj.detail = detail
            except Exception as e:
                obj.detail = str(detail)

            if exc_traceback:
                obj.traceback = traceback.format_tb(exc_traceback)
            obj.save()
            return obj
        except Exception as exc:
            raise GeneralEventCreateError(
                f"Unable to create general event ({exception} {exc_traceback}). EXCEPTION {exc}"
            )
