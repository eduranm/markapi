from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from config.menu import get_menu_order

from .models import XMLDocument
from . import urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('xml-manager/', include(urls)),
    ]


class XMLDocumentSnippetViewSet(SnippetViewSet):
    model = XMLDocument
    verbose_name = _("XML Document")
    verbose_name_plural = _("XML Documents")
    icon = "folder-open-inverse"
    menu_name = "xml_manager"
    menu_label = _("XML Document")
    menu_order = get_menu_order("xml_manager")
    add_to_admin_menu = True

    list_display = (
        "xml_file",
        "validation_file",
        "exceptions_file",
        "pdf_file",
        "html_file",
        "uploaded_at",
    )
    list_filter = (
    )
    search_fields = (
        "xml_file",
    )


register_snippet(XMLDocumentSnippetViewSet)

@hooks.register('register_admin_menu_item')
def register_process_form_menu_item():
    return MenuItem(
        _('Process XML'),
        '/admin/xml-manager/upload/',
        icon_name='form',
        order=get_menu_order("xml_manager") + 1,
    )
