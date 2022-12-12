"""
Tests for tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Url for tag id"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(email, password)


def create_tag(user, **params):
    """Helper fucntion to create new tag"""

    defaults = {
        'name': 'Tag1',
        'description': 'Test Tag'
    }

    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)
    return tag


class PublicTagApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieve tags list"""

        create_tag(user=self.user)
        create_tag(user=self.user, name="Tag2")
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, res.status_code)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags limited to user"""

        user2 = create_user(email='user2@example.com')
        create_tag(user=user2, name='Alpha')
        tag = create_tag(user=self.user, name='Beta')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test update tag API"""

        tag = create_tag(user=self.user)

        payload = {'name': 'Update Tag'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test delete tag API"""

        tag = create_tag(user=self.user)
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
