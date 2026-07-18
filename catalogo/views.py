from django.db.models import Count
from django.db.models.deletion import ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Autor, Libro
from .serializers import AutorSerializer, LibroSerializer


@api_view(["GET"])
def api_inicio(request):
    """
    Endpoint inicial para comprobar que la API está funcionando.
    """
    return Response(
        {
            "mensaje": "API de gestión de libros funcionando correctamente",
            "version": "1.0.0",
            "endpoints": {
                "autores": "/api/autores/",
                "libros": "/api/libros/",
            },
        },
        status=status.HTTP_200_OK,
    )


class AutorViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de autores.
    """

    serializer_class = AutorSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "nombre",
        "apellido",
        "nacionalidad",
    ]

    ordering_fields = [
        "id",
        "nombre",
        "apellido",
        "nacionalidad",
        "creado_en",
        "total_libros",
    ]

    ordering = [
        "apellido",
        "nombre",
    ]

    def get_queryset(self):
        queryset = (
            Autor.objects
            .annotate(total_libros=Count("libros"))
            .prefetch_related("libros")
        )

        activo = self.request.query_params.get("activo")

        if activo is not None:
            valor = activo.lower()

            if valor in ("true", "1", "si", "sí"):
                queryset = queryset.filter(activo=True)

            elif valor in ("false", "0", "no"):
                queryset = queryset.filter(activo=False)

        return queryset

    def destroy(self, request, *args, **kwargs):
        autor = self.get_object()

        try:
            autor.delete()

        except ProtectedError:
            return Response(
                {
                    "detalle": (
                        "No se puede eliminar el autor porque tiene "
                        "libros relacionados."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class LibroViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de libros.
    """

    serializer_class = LibroSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "titulo",
        "isbn",
        "genero",
        "idioma",
        "autor__nombre",
        "autor__apellido",
    ]

    ordering_fields = [
        "id",
        "titulo",
        "fecha_publicacion",
        "numero_paginas",
        "creado_en",
    ]

    ordering = ["titulo"]

    def get_queryset(self):
        queryset = Libro.objects.select_related("autor")

        autor_id = self.request.query_params.get("autor")
        genero = self.request.query_params.get("genero")
        idioma = self.request.query_params.get("idioma")
        disponible = self.request.query_params.get("disponible")

        if autor_id:
            queryset = queryset.filter(autor_id=autor_id)

        if genero:
            queryset = queryset.filter(genero__iexact=genero)

        if idioma:
            queryset = queryset.filter(idioma__iexact=idioma)

        if disponible is not None:
            valor = disponible.lower()

            if valor in ("true", "1", "si", "sí"):
                queryset = queryset.filter(disponible=True)

            elif valor in ("false", "0", "no"):
                queryset = queryset.filter(disponible=False)

        return queryset