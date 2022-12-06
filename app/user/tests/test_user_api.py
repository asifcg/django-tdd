"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)."""

    def setUp(self):
        """Setup for tests."""
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful."""
        payload = {
            'email': 'user1@example.com',
            'password': 'Testpass123',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails."""
        payload = {
            'email': 'test1@example.com',
            'password': 'Testpass123',
            'name': 'Test User'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters."""
        payload = {
            'email': 'shortpass@example.com',
            'password': 'pw',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test Create token API for user"""
        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Testpass123'
        }

        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'Testpass123'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_bad_credentials(self):
        """Test returns error if credentials invalid"""
        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'goodpass'
        }

        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'badpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_nonexistent_user(self):
        """Test returns error if user doesn't exist"""
        payload = {
            'email': 'test@example.com',
            'password': 'goodpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        """Setup for tests."""
        self.user = create_user(
            email='test@example.com',
            password='Testpass123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user."""
        payload = {
            'name': 'New Name',
            'password': 'Newpass123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_profile_with_invalid_password(self):
        """Test updating the user profile for authenticated user."""
        payload = {
            'name': 'New Name',
            'password': 'new'
        }

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_authorized_with_valid_token(self):
        """Test that authentication is required for users."""
        user_details = {'email': 'test@example.com', 'password': 'Testpass123'}
        user = self.user

        res = self.client.post(TOKEN_URL, user_details)
        token = res.data['token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': user.name,
            'email': user.email
        })

    def test_me_unauthorized_with_invalid_token(self):
        """Test that authentication is required for users."""

        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
