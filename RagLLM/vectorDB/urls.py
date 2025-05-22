from django.urls import path
from .views import *

app_name = "vectorDB"

urlpatterns = [path("upload/", CreateDocumentView.as_view(), name="upload_document")]
