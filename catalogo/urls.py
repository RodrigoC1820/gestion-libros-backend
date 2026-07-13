from django.urls import path

from .views import api_inicio


app_name = "catalogo"

urlpatterns = [
    path("", api_inicio, name="api-inicio"),
]