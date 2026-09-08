"""
Serializer for the recipe model.
"""

from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "time_minutes",
            "price",
            "description",
            "link",
        )
        read_only_fields = ["id"]
