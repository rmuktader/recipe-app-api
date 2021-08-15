from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import recipe_image_file_path
from core.factories import IngredientFactory, TagFactory, RecipeFactory, UserFactory


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
        tag = TagFactory.create(user=UserFactory.create())

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test ingredient string representaion"""
        ingredient = IngredientFactory.create(user=UserFactory.create())

        self.assertEqual(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = RecipeFactory.create(
            user=UserFactory.create(), title="Steak and musroom sauce", time_minutes=5, price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that" image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, "myimage.jpg")

        expected_path = f"uploads/recipe/{uuid}.jpg"
