from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AutorViewSet, LibroViewSet, api_inicio


app_name = "catalogo"

router = DefaultRouter()

router.register(
    "autores",
    AutorViewSet,
    basename="autor",
)

router.register(
    "libros",
    LibroViewSet,
    basename="libro",
)

urlpatterns = [
    path("", api_inicio, name="api-inicio"),
    path("", include(router.urls)),
]