from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages

from .tasks import task_process_xml_document
from .models import XMLDocument


def upload_xml_page(request):
    return render(request, "xml_manager/process_form.html")


@require_POST
@csrf_exempt
def process_xml(request):
    xml_file = request.FILES.get('xml_file')
    if not xml_file:
        messages.error(request, "Arquivo não enviado.")
        return redirect(reverse('upload_xml_page'))

    xml_obj = XMLDocument.objects.create(xml_file=xml_file)

    task_process_xml_document.delay(xml_obj.id)

    messages.success(request, "Arquivo enviado para processamento!")
    return redirect(reverse('upload_xml_page'))
