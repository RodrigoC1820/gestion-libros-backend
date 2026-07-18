from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Autor, Libro


class CatalogoAPITestCase(APITestCase):
    def setUp(self):
        usuario_modelo = get_user_model()

        self.usuario = usuario_modelo.objects.create_user(
            username="usuario_prueba",
            password="Password123!",
        )

        self.aplicacion = Application.objects.create(
            name="Aplicación de pruebas",
            user=self.usuario,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )

        self.token = AccessToken.objects.create(
            user=self.usuario,
            application=self.aplicacion,
            token="token-prueba-seguro",
            expires=timezone.now() + timedelta(hours=1),
            scope="read write",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token.token}"
        )

        self.autor = Autor.objects.create(
            nombre="Gabriel",
            apellido="García Márquez",
            nacionalidad="Colombiana",
            fecha_nacimiento="1927-03-06",
            biografia="Escritor colombiano.",
            activo=True,
        )

        self.libro = Libro.objects.create(
            autor=self.autor,
            titulo="Cien años de soledad",
            isbn="9780307474728",
            genero="Novela",
            fecha_publicacion="1967-05-30",
            numero_paginas=417,
            idioma="Español",
            disponible=True,
        )

    def test_listar_autores_con_token(self):
        respuesta = self.client.get(reverse("catalogo:autor-list"))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)

    def test_endpoint_protegido_sin_token(self):
        self.client.credentials()

        respuesta = self.client.get(reverse("catalogo:autor-list"))

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_crear_autor(self):
        datos = {
            "nombre": "Isabel",
            "apellido": "Allende",
            "nacionalidad": "Chilena",
            "fecha_nacimiento": "1942-08-02",
            "biografia": "Escritora chilena.",
            "activo": True,
        }

        respuesta = self.client.post(
            reverse("catalogo:autor-list"),
            datos,
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Autor.objects.filter(
                nombre="Isabel",
                apellido="Allende",
            ).exists()
        )

    def test_rechazar_fecha_nacimiento_futura(self):
        datos = {
            "nombre": "Autor",
            "apellido": "Futuro",
            "nacionalidad": "Ecuatoriana",
            "fecha_nacimiento": "2099-01-01",
            "biografia": "",
            "activo": True,
        }

        respuesta = self.client.post(
            reverse("catalogo:autor-list"),
            datos,
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("fecha_nacimiento", respuesta.data)

    def test_listar_libros(self):
        respuesta = self.client.get(reverse("catalogo:libro-list"))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)

    def test_crear_libro(self):
        datos = {
            "autor": self.autor.id,
            "titulo": "El amor en los tiempos del cólera",
            "isbn": "9780307389732",
            "genero": "Novela",
            "fecha_publicacion": "1985-01-01",
            "numero_paginas": 368,
            "idioma": "Español",
            "disponible": True,
        }

        respuesta = self.client.post(
            reverse("catalogo:libro-list"),
            datos,
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_201_CREATED,
        )

    def test_rechazar_isbn_invalido(self):
        datos = {
            "autor": self.autor.id,
            "titulo": "Libro de prueba",
            "isbn": "ABC123",
            "genero": "Prueba",
            "fecha_publicacion": "2024-01-01",
            "numero_paginas": 100,
            "idioma": "Español",
            "disponible": True,
        }

        respuesta = self.client.post(
            reverse("catalogo:libro-list"),
            datos,
            format="json",
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("isbn", respuesta.data)

    def test_no_eliminar_autor_con_libros(self):
        respuesta = self.client.delete(
            reverse(
                "catalogo:autor-detail",
                kwargs={"pk": self.autor.id},
            )
        )

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_409_CONFLICT,
        )
        self.assertTrue(
            Autor.objects.filter(id=self.autor.id).exists()
        )