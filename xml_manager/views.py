from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404

from .tasks import task_process_xml_document
from .models import XMLDocument


@staff_member_required
def process_xml_pk(request, pk):
    obj = get_object_or_404(XMLDocument, pk=pk)
    task_process_xml_document.delay(obj.id)
    messages.success(request, f"XML {obj.id} enviado para processamento")
    return redirect("/admin/snippets/xml_manager/xmldocument/")
