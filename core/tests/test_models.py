from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import recipe_image_file_path
from core.factories import IngredientFactory, TagFactory, RecipeFactory


def sample_user(email="test@test.com", password="password123"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def setUp(self) -> None:
        TagFactory.reset_sequence()
        IngredientFactory.reset_sequence()

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@gmail.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for  a new user is normalized"""
        email = email = "test@GMAIL.com"
        user = get_user_model().objects.create_user(email=email, password="test")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, password="pass123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser("test1@gmail.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representaion"""
        tag = TagFactory.create(user=sample_user())

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test ingredient string representaion"""
        ingredient = IngredientFactory.create(user=sample_user())

        self.assertEqual(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = RecipeFactory.create(user=sample_user(), title="Steak and musroom sauce", time_minutes=5, price=5.00)

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that" image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, "myimage.jpg")

        expected_path = f"uploads/recipe/{uuid}.jpg"
