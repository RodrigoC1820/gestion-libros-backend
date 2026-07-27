from django.db.models import Count
from django.db.models.deletion import ProtectedError

from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
)
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response

from .models import Autor, Categoria, Libro
from .permissions import LecturaPublicaEscrituraAutenticada
from .serializers import (
    AutorSerializer,
    CategoriaSerializer,
    LibroSerializer,
)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_inicio(request):
    """
    Endpoint inicial para comprobar que la API funciona correctamente.
    """

    return Response(
        {
            "mensaje": (
                "API de gestión de libros "
                "funcionando correctamente"
            ),
            "version": "1.0.0",
            "endpoints": {
                "autores": "/api/autores/",
                "libros": "/api/libros/",
                "libros_destacados": (
                    "/api/libros/destacados/"
                ),
                "categorias": "/api/categorias/",
                "obtener_token": "/o/token/",
                "revocar_token": "/o/revoke_token/",
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def listar_categorias(request):
    """
    Devuelve las categorías activas registradas en el sistema.
    """

    categorias = (
        Categoria.objects
        .filter(activa=True)
        .order_by("nombre")
    )

    serializer = CategoriaSerializer(
        categorias,
        many=True,
        context={
            "request": request,
        },
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


class AutorViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de autores.
    """

    serializer_class = AutorSerializer

    permission_classes = [
        LecturaPublicaEscrituraAutenticada,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

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
        """
        Devuelve autores con el total de libros relacionados.

        Permite:

        /api/autores/?activo=true
        /api/autores/?activo=false
        """

        queryset = (
            Autor.objects
            .annotate(
                total_libros=Count("libros"),
            )
            .prefetch_related("libros")
        )

        activo = self.request.query_params.get(
            "activo",
        )

        if activo is not None:
            valor = activo.lower()

            if valor in (
                "true",
                "1",
                "si",
                "sí",
            ):
                queryset = queryset.filter(
                    activo=True,
                )

            elif valor in (
                "false",
                "0",
                "no",
            ):
                queryset = queryset.filter(
                    activo=False,
                )

        return queryset

    def destroy(self, request, *args, **kwargs):
        """
        Impide eliminar un autor que tenga libros relacionados.
        """

        autor = self.get_object()

        try:
            autor.delete()

        except ProtectedError:
            return Response(
                {
                    "detalle": (
                        "No se puede eliminar el autor porque "
                        "tiene libros relacionados."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class LibroViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de libros.
    """

    serializer_class = LibroSerializer

    permission_classes = [
        LecturaPublicaEscrituraAutenticada,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

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

    ordering = [
        "titulo",
    ]

    def get_queryset(self):
        """
        Devuelve los libros con su autor relacionado.

        Permite filtros como:

        /api/libros/?autor=1
        /api/libros/?genero=Novela
        /api/libros/?idioma=Español
        /api/libros/?disponible=true
        """

        queryset = (
            Libro.objects
            .select_related("autor")
            .all()
        )

        autor_id = self.request.query_params.get(
            "autor",
        )
        genero = self.request.query_params.get(
            "genero",
        )
        idioma = self.request.query_params.get(
            "idioma",
        )
        disponible = self.request.query_params.get(
            "disponible",
        )

        if autor_id:
            queryset = queryset.filter(
                autor_id=autor_id,
            )

        if genero:
            queryset = queryset.filter(
                genero__iexact=genero,
            )

        if idioma:
            queryset = queryset.filter(
                idioma__iexact=idioma,
            )

        if disponible is not None:
            valor = disponible.lower()

            if valor in (
                "true",
                "1",
                "si",
                "sí",
            ):
                queryset = queryset.filter(
                    disponible=True,
                )

            elif valor in (
                "false",
                "0",
                "no",
            ):
                queryset = queryset.filter(
                    disponible=False,
                )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[
            permissions.AllowAny,
        ],
        url_path="destacados",
    )
    def destacados(self, request):
        """
        Devuelve hasta cuatro libros disponibles.
        """

        libros = (
            self.get_queryset()
            .filter(disponible=True)
            .order_by("-creado_en")[:4]
        )

        serializer = self.get_serializer(
            libros,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )