from django.test import SimpleTestCase
from rest_framework.test import APIClient


# Create your tests here.
class TestViews(SimpleTestCase):

    def test_posts(self):
        """Test Get Posts"""
        client = APIClient()
        res = client.get('/posts/')

        data = res.json()
        self.assertEqual(res.status_code, 200)
        hasPostsKey = True if data.get("posts") else False
        self.assertTrue(hasPostsKey)
