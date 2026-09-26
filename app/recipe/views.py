"""
Views for the recipe APIs
"""

from rest_framework import viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)


from core.models import Recipe, Tag, Ingredient
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="tags",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated list of tag IDs to filter by.",
            ),
            OpenApiParameter(
                name="ingredients",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Comma-separated list of ingredient IDs to filter by."
                ),
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        queryset = self.queryset.filter(user=self.request.user)
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")

        if tags:
            queryset = queryset.filter(tags__id__in=tags.split(","))
        if ingredients:
            queryset = queryset.filter(
                ingredients__id__in=ingredients.split(",")
            )

        return queryset.distinct().order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve queryset for authenticated user."""
        queryset = self.queryset.filter(user=self.request.user)
        if self.request.query_params.get("assigned_only") == "1":
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.order_by("-name").distinct()


_ASSIGNED_ONLY_PARAMETER = OpenApiParameter(
    name="assigned_only",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description="Set to 1 to return only attributes used by a recipe.",
    enum=[0, 1],
)


@extend_schema_view(list=extend_schema(parameters=[_ASSIGNED_ONLY_PARAMETER]))
class TagViewSet(BaseRecipeAttrViewSet):
    """View for manage tag APIs."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


@extend_schema_view(list=extend_schema(parameters=[_ASSIGNED_ONLY_PARAMETER]))
class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
