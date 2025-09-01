from django.urls import path
from . import views


urlpatterns = [
    path("process/<int:pk>/", views.process_xml_pk, name="process_xml_pk"),
]