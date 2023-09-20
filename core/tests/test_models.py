"""
Test for models.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_image(self):
        """Test creating an image is successful"""
        user = get_user_model().objects.create_user("test@example.com", "testpass123")
        image = models.Image.objects.create(user=user, file="test.jpg")
        self.assertEqual(user, image.user)
        