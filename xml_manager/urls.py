from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.upload_xml_page, name='upload_xml_page'),
    path('process/', views.process_xml, name='process_xml'),
]
