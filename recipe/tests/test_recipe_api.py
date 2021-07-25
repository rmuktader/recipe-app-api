from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Main course"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return sample recipe"""
    defaults = {"title": "Sample recipe", "time_minutes": 10, "price": 5.00}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


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

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_recipe_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user("test2@test.com", "test12344")
        sample_recipe(self.user)
        sample_recipe(user2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

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
        tag1 = sample_tag(self.user, name="Vegan")
        tag2 = sample_tag(self.user, name="Dessert")
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
        ingredient1 = sample_ingredient(self.user, name="Prawns")
        ingredient2 = sample_ingredient(self.user, name="Ginger")
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
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        new_tag = sample_tag(self.user, name="Curry")

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
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        payload = {"title": "Spaghetti carbonara", "time_minutes": 25, "price": 5.00}
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, res.data["title"])
        self.assertEqual(recipe.time_minutes, res.data["time_minutes"])
        self.assertEqual(str(recipe.price), str(res.data["price"]))
        self.assertEqual(recipe.tags.count(), 0)
