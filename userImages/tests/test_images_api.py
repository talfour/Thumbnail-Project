"""
Test for images APIs.
"""
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APIClient

from core.models import CustomTier, Image
from userImages import serializers

MEDIA_ROOT = tempfile.mkdtemp()

IMAGES_URL = reverse("image-list")


def detail_url(image_id):
    """Create and return an image detail URL."""
    return reverse("image-detail", args=[image_id])


def temporary_image():
    """Create and returns a temporary image."""
    bts = BytesIO()
    img = PILImage.new("RGB", (100, 100))
    img.save(bts, "png")
    return SimpleUploadedFile("test.png", bts.getvalue())


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create(**params)


def create_image(user, **params):
    """Create and return a sample image"""
    defaults = {"file": temporary_image()}
    defaults.update(params)

    image = Image.objects.create(user=user, **defaults)
    return image


class PublicImageAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(IMAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PrivateImageAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password="test123!")
        self.client.force_authenticate(self.user)

    @classmethod
    def tearDownClass(self):
        """Remove all test files after tests are finished."""
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_retrieve_images(self):
        """Test retrieving a list of images."""
        create_image(user=self.user)
        create_image(user=self.user)

        res = self.client.get(IMAGES_URL)

        images = Image.objects.all().order_by("-id")
        serializer = serializers.ImageSerializer(images, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        domain_url = "http://testserver"

        # Update the file field URLs in the serializer data
        for data in serializer.data:
            data["file"] = domain_url + data["file"]
        self.assertEqual(res.data, serializer.data)

    def test_image_list_limited_to_user(self):
        """Test list of images is limited to authenticated user."""
        other_user = create_user(email="other@example.com", password="testpass123")
        create_image(user=other_user)
        create_image(user=self.user)

        res = self.client.get(IMAGES_URL)

        images = Image.objects.filter(user=self.user)
        serializer = serializers.ImageSerializer(images, many=True)
        domain_url = "http://testserver"

        # Update the file field URLs in the serializer data
        for data in serializer.data:
            data["file"] = domain_url + data["file"]
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_image(self):
        """Test creating an image."""

        payload = {"file": temporary_image()}

        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        image = Image.objects.first()
        self.assertEqual(image.user, self.user)

    def test_access_other_users_image_error(self):
        """Test trying to access another user image gives error."""
        new_user = create_user(email="test123@example.com", password="testpassa123")
        image = create_image(user=new_user)

        url = detail_url(image.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Image.objects.filter(id=image.id).exists())

    def test_thumbnail_basic_is_created(self):
        """Test that thumbnail is created for basic user and original file link is not included."""
        self.user.tier = "Basic"
        self.user.save()
        payload = {"file": temporary_image()}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["file"], None)
        self.assertTrue(res.data["thumbnail_200px"] != None)

    def test_thumbnail_premium_is_created(self):
        """Test that both thumbnails are created and link exists for Premium user."""
        self.user.tier = "Premium"
        self.user.save()
        payload = {"file": temporary_image()}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["file"] != None)
        self.assertTrue(res.data["thumbnail_200px"] != None)
        self.assertTrue(res.data["thumbnail_400px"] != None)

    def test_thumbnail_expire_link_is_created_for_enterprise(self):
        """Test creating expire link for Enterprise user."""
        self.user.tier = "Enterprise"
        self.user.save()
        payload = {"file": temporary_image(), "expiration_time": 3000}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["expiration_image"] != None)

    def test_thumbnail_expire_link_seconds_validation(self):
        """Test creating expire link for Enterprise user."""
        self.user.tier = "Enterprise"
        self.user.save()
        payload = {"file": temporary_image(), "expiration_time": 3}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {"file": temporary_image(), "expiration_time": 7000000}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_custom_tier_user_works(self):
        """Test custom user tier with different configurations."""

        custom_tier = CustomTier.objects.create(
            name="Custom Tier",
            thumbnail_sizes=600,
            include_original_link=False,
            generate_expiring_links=True,
        )
        self.user.custom_tier = custom_tier
        self.user.save()

        payload = {"file": temporary_image(), "expiration_time": 300}
        res = self.client.post(IMAGES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["file"], None)
        self.assertTrue(res.data["custom_thumbnail"] != None)
