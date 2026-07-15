from datetime import date

from rest_framework import serializers

from .models import Autor, Libro


class LibroResumenSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para mostrar los libros relacionados con un autor.
    """

    class Meta:
        model = Libro
        fields = (
            "id",
            "titulo",
            "isbn",
            "genero",
            "disponible",
        )


class AutorSerializer(serializers.ModelSerializer):
    libros = LibroResumenSerializer(
        many=True,
        read_only=True,
    )
    nombre_completo = serializers.SerializerMethodField()
    total_libros = serializers.SerializerMethodField()

    class Meta:
        model = Autor
        fields = (
            "id",
            "nombre",
            "apellido",
            "nombre_completo",
            "nacionalidad",
            "fecha_nacimiento",
            "biografia",
            "activo",
            "libros",
            "total_libros",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "nombre_completo",
            "libros",
            "total_libros",
            "creado_en",
            "actualizado_en",
        )

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"

    def get_total_libros(self, obj):
        return obj.libros.count()

    def validate_nombre(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres."
            )

        return value.title()

    def validate_apellido(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "El apellido debe tener al menos 2 caracteres."
            )

        return value.title()

    def validate_fecha_nacimiento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede ser futura."
            )

        return value


class LibroSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(
        source="autor.__str__",
        read_only=True,
    )

    class Meta:
        model = Libro
        fields = (
            "id",
            "autor",
            "autor_nombre",
            "titulo",
            "isbn",
            "genero",
            "fecha_publicacion",
            "numero_paginas",
            "idioma",
            "disponible",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "autor_nombre",
            "creado_en",
            "actualizado_en",
        )

    def validate_titulo(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                "El título debe tener al menos 2 caracteres."
            )

        return value

    def validate_isbn(self, value):
        isbn_limpio = (
            value.replace("-", "")
            .replace(" ", "")
            .strip()
        )

        if not isbn_limpio.isdigit():
            raise serializers.ValidationError(
                "El ISBN solo debe contener números, espacios o guiones."
            )

        if len(isbn_limpio) not in (10, 13):
            raise serializers.ValidationError(
                "El ISBN debe contener 10 o 13 números."
            )

        return isbn_limpio

    def validate_fecha_publicacion(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha de publicación no puede ser futura."
            )

        return value

    def validate_numero_paginas(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "El libro debe tener al menos una página."
            )

        return value

    def validate_autor(self, value):
        if not value.activo:
            raise serializers.ValidationError(
                "No se puede asignar un libro a un autor inactivo."
            )

        return value