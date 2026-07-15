from django.contrib import admin

from .models import Autor, Libro


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "apellido",
        "nacionalidad",
        "activo",
        "creado_en",
    )
    search_fields = (
        "nombre",
        "apellido",
        "nacionalidad",
    )
    list_filter = (
        "activo",
        "nacionalidad",
    )
    ordering = (
        "apellido",
        "nombre",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "autor",
        "isbn",
        "genero",
        "idioma",
        "disponible",
    )
    search_fields = (
        "titulo",
        "isbn",
        "autor__nombre",
        "autor__apellido",
    )
    list_filter = (
        "genero",
        "idioma",
        "disponible",
    )
    ordering = ("titulo",)
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    autocomplete_fields = ("autor",)