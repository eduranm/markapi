from config import celery_app
from reference.marker import mark_references
from reference.models import Reference, ElementCitation
import json

@celery_app.task()
def get_reference(obj_id):
    obj_reference = Reference.objects.get(id=obj_id)
    marked = mark_references(obj_reference.mixed_citation)
    for item in marked:
        for i in item['choices']:
            ElementCitation.objects.create(
                reference=obj_reference,
                marked=i
            )
    obj_reference.estatus = 2
    obj_reference.save()