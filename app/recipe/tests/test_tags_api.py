"""
Test tags API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Return tag detail URL"""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the private tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Carnivorous")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_tags_by_assigned_only(self):
        """Test returning only tags assigned to a recipe."""
        assigned_tag = Tag.objects.create(user=self.user, name="Vegan")
        unassigned_tag = Tag.objects.create(user=self.user, name="Dessert")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Sample recipe",
            time_minutes=10,
            price=1,
        )
        recipe.tags.add(assigned_tag)
        another_recipe = Recipe.objects.create(
            user=self.user,
            title="Another recipe",
            time_minutes=15,
            price=2,
        )
        another_recipe.tags.add(assigned_tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual([tag["id"] for tag in res.data], [assigned_tag.id])
        self.assertNotIn(unassigned_tag.id, [tag["id"] for tag in res.data])

    def test_tags_limited_to_user(self):
        """Test that tags are limited to the authenticated user"""
        other_user = create_user(
            email="other@example.com", password="testpass123"
        )
        Tag.objects.create(user=other_user, name="Carnivorous")
        tag = Tag.objects.create(user=self.user, name="Vegan")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name="Dinner")
        url = detail_url(tag.id)
        payload = {"name": "New tag name"}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="Cake")
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
