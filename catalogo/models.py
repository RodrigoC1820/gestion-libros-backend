from django.core.validators import MinValueValidator
from django.db import models


class Autor(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name="nombre",
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name="apellido",
    )
    nacionalidad = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="nacionalidad",
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de nacimiento",
    )
    biografia = models.TextField(
        blank=True,
        verbose_name="biografía",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    foto = models.ImageField(
        upload_to="autores/",
        null=True,
        blank=True,
        verbose_name="foto",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="última actualización",
    )

    class Meta:
        verbose_name = "autor"
        verbose_name_plural = "autores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Libro(models.Model):
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT,
        related_name="libros",
        verbose_name="autor",
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="título",
    )
    isbn = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ISBN",
    )
    genero = models.CharField(
        max_length=80,
        verbose_name="género",
    )
    fecha_publicacion = models.DateField(
        verbose_name="fecha de publicación",
    )
    numero_paginas = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="número de páginas",
    )
    idioma = models.CharField(
        max_length=40,
        default="Español",
        verbose_name="idioma",
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name="disponible",
    )

    portada = models.ImageField(
        upload_to="libros/",
        null=True,
        blank=True,
        verbose_name="portada",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="última actualización",
    )

    class Meta:
        verbose_name = "libro"
        verbose_name_plural = "libros"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo

class Categoria(models.Model):
    nombre = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="nombre",
    )
    imagen = models.ImageField(
        upload_to="categorias/",
        null=True,
        blank=True,
        verbose_name="imagen",
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="activa",
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="última actualización",
    )

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre