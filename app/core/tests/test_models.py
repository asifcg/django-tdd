"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test for models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@example.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='Testpass123'
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Testpass123')

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
            'superuser@example.com',
            'Testpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe."""

        user = get_user_model().objects.create_user(
            'test@example.com',
            'Testpass123',
        )

        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00,
            'user': user,
        }
        recipe = models.Recipe.objects.create(**payload)

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

    def test_create_tag(self):
        """Test creating a tag."""

        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Vegan',
            description='Vegan food',
        )

        self.assertEqual(str(tag), tag.name)
