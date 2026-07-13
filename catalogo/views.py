from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def api_inicio(request):
    """
    Comprueba que la API REST se encuentra disponible.
    """
    return Response(
        {
            "mensaje": "API de gestión de libros funcionando correctamente",
            "version": "1.0.0",
        },
        status=status.HTTP_200_OK,
    )