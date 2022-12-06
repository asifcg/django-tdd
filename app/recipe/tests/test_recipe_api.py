"""
Tests for the recipe API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from decimal import Decimal
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_recipe_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):

    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': Decimal(10.4)
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTest(TestCase):
    """Test unautherized API requests"""

    def test_auth_required(self):
        """Test that auth is required"""

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@exaple.com',
            'Testpass123',
        )

        self.client.force_authenticate(self.user)

    def test_reterive_recipes(self):
        """Test retrieving a list of recipes"""

        create_recipe(user=self.user)
        create_recipe(user=self.user, title='Test Recipe 2')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""

        user2 = get_user_model().objects.create_user(
            'user2@example.com',
            'Testpass123',
        )

        create_recipe(user=user2)
        create_recipe(user=self.user, title='Test Recipe 2')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""

        recipe = create_recipe(user=self.user)

        url = detail_recipe_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_detail_not_found(self):
        """Test that recipe detail not found"""

        url = detail_recipe_url(1)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data, {'detail': 'Not found.'})

    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': Decimal(5.5)
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_delete_recipe(self):
        """Test deleting a recipe"""

        recipe = create_recipe(user=self.user)
        url = detail_recipe_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_update_recipe(self):
        """Test updating a recipe"""

        recipe = create_recipe(user=self.user)
        url = detail_recipe_url(recipe.id)
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': Decimal(5.5)
        }
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""

        original_price = round(Decimal(10.40), 2)
        recipe = create_recipe(user=self.user, price=original_price)
        url = detail_recipe_url(recipe.id)
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
        }
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        print(recipe.price)
        print(original_price)
        self.assertEqual(recipe.price, original_price)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""

        original_price = round(Decimal(10.40), 2)
        recipe = create_recipe(user=self.user, price=original_price)
        url = detail_recipe_url(recipe.id)
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': Decimal(5.5)
        }
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        self.assertNotEqual(recipe.price, original_price)
