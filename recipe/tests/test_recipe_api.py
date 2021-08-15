import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from core.factories import IngredientFactory, RecipeFactory, TagFactory
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


class PublicRecipeApiTests(TestCase):
    """Test unauthorized recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authorized receipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "testpass1234")
        self.client.force_authenticate(self.user)
        TagFactory.reset_sequence()
        IngredientFactory.reset_sequence()
        RecipeFactory.reset_sequence()

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        RecipeFactory.create(user=self.user)
        RecipeFactory.create(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_recipe_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user("test2@test.com", "test12344")
        RecipeFactory.create(user=self.user)
        RecipeFactory.create(user=user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = RecipeFactory.create(user=self.user)
        recipe.tags.add(TagFactory.create(user=self.user))
        recipe.ingredients.add(IngredientFactory.create(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(serializer.data, res.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {"title": "Chocolate cheesecake", "time_minutes": 30, "price": 5.00}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(str(res.data[key]), str(getattr(recipe, key)))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags"""
        tag1 = TagFactory.create(user=self.user)
        tag2 = TagFactory.create(user=self.user)
        payload = {"title": "Avacado lime cheesecake", "time_minutes": 30, "tags": [tag1.id, tag2.id], "price": 20.00}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test create recipe with ingredients"""
        ingredient1 = IngredientFactory.create(user=self.user)
        ingredient2 = IngredientFactory.create(user=self.user)
        payload = {
            "title": "Thai prawn red curry",
            "ingredients": (ingredient1.id, ingredient2.id),
            "time_minutes": 20,
            "price": 7.00,
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = RecipeFactory.create(user=self.user)
        recipe.tags.add(TagFactory.create(user=self.user))
        new_tag = TagFactory.create(user=self.user)

        payload = {"title": "Chicken tikka", "tags": [new_tag.id]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, res.data["title"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = RecipeFactory.create(user=self.user)
        recipe.tags.add(TagFactory.create(user=self.user))
        payload = {"title": "Spaghetti carbonara", "time_minutes": 25, "price": 5.00}
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, res.data["title"])
        self.assertEqual(recipe.time_minutes, res.data["time_minutes"])
        self.assertEqual(str(recipe.price), str(res.data["price"]))
        self.assertEqual(recipe.tags.count(), 0)


class RecipeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user1@test.com", "testpass123")
        self.client.force_authenticate(self.user)
        self.recipe = RecipeFactory.create(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def xtest_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "notimage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = RecipeFactory.create(user=self.user, title="Thai vegetable curry")
        recipe2 = RecipeFactory.create(user=self.user, title="Eggplant with tahini")
        tag1 = TagFactory.create(user=self.user)
        tag2 = TagFactory.create(user=self.user)
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = RecipeFactory.create(user=self.user, title="Fish and chips")

        res = self.client.get(RECIPES_URL, {"tags": f"{tag1.id},{tag2.id}"})
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_by_ingredients(self):
        """Test returning recipe with specific ingredients"""
        recipe1 = RecipeFactory.create(user=self.user, title="Posh beans on toast")
        recipe2 = RecipeFactory.create(user=self.user, title="Chicken caccatori")
        ingredient1 = IngredientFactory.create(user=self.user)
        ingredient2 = IngredientFactory.create(user=self.user)
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = RecipeFactory.create(user=self.user, title="Steak and mushrooms")

        res = self.client.get(RECIPES_URL, {"ingredients": f"{ingredient1.id},{ingredient2.id}"})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
