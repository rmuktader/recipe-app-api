from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from core.factories import TagFactory
from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApitests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user("test@test.com", "password123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        TagFactory.reset_sequence()

    def test_retrive_tags(self):
        """Test retrieving tags"""
        TagFactory.create(user=self.user, name="Vegan")
        TagFactory.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user("other@test.com", "password123")
        TagFactory.create(user=user2, name="Fruity")
        tag = TagFactory.create(user=self.user, name="Baked")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {"name": "New Tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user, name=payload["name"]).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = TagFactory.create(user=self.user, name="Breakfast")
        tag2 = TagFactory.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(user=self.user, title="Coriander eggs on toast", time_minutes=10, price=5.00)
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
