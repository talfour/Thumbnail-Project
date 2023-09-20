import os

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from core.tasks import create_thumbnail

from .utils import generate_expiring_link


class BaseImageProcessor:
    def create_thumbnail(self, instance, thumbnail_suffix, thumbnail_size=None):
        image_path = instance.file.path
        thumbnail_filename = (
            os.path.splitext(os.path.basename(image_path))[0] + thumbnail_suffix
        )
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "images", thumbnail_filename)

        create_thumbnail.delay(image_path, thumbnail_path, thumbnail_size)
        return os.path.relpath(thumbnail_path, start=settings.MEDIA_ROOT)


class BasicImageProcessor(BaseImageProcessor):
    def process_image(self, instance):
        instance.thumbnail_200px = self.create_thumbnail(
            instance, "_thumbnail_200px.jpg", 200
        )


class PremiumImageProcessor(BaseImageProcessor):
    def process_image(self, instance):
        instance.thumbnail_200px = self.create_thumbnail(
            instance, "_thumbnail_200px.jpg", 200
        )
        instance.thumbnail_400px = self.create_thumbnail(
            instance, "_thumbnail_400px.jpg", 400
        )


class EnterpriseImageProcessor(BaseImageProcessor):
    def process_image(self, instance, request):
        instance.thumbnail_200px = self.create_thumbnail(
            instance, "_thumbnail_200px.jpg", 200
        )
        instance.thumbnail_400px = self.create_thumbnail(
            instance, "_thumbnail_400px.jpg", 400
        )
        self.request = request
        expiration_seconds = self.request.data.get("expiration_time")
        if expiration_seconds is None or not expiration_seconds.strip():
            expiration_seconds = None

        if expiration_seconds is not None:
            expiration_seconds = int(expiration_seconds)
            expiration_time = timezone.now() + timezone.timedelta(
                seconds=expiration_seconds
            )

            # Generate the expiring link
            expiring_link = generate_expiring_link(instance.file.url, expiration_time)

            # Include the expiring link
            full_url = self.request.build_absolute_uri(
                reverse("expiring-image", args=[expiring_link])
            )
            instance.expiration_image = full_url


class CustomImageProcessor(BaseImageProcessor):
    def process_image(self, instance, user_tier, request):
        thumbnail_size = int(user_tier.thumbnail_sizes)
        instance.custom_thumbnail = self.create_thumbnail(
            instance, f"_thumbnail_{thumbnail_size}px.jpg", thumbnail_size
        )

        link_to_original_file = user_tier.include_original_link
        generate_expiring_links = user_tier.generate_expiring_links

        if generate_expiring_links:
            expiration_seconds = request.data.get("expiration_time")

        if expiration_seconds is None or not expiration_seconds.strip():
            expiration_seconds = None

        if expiration_seconds is not None:
            expiration_seconds = int(expiration_seconds)
            expiration_time = timezone.now() + timezone.timedelta(
                seconds=expiration_seconds
            )

            # Generate the expiring link
            expiring_link = generate_expiring_link(instance.file.url, expiration_time)

            # Include the expiring link
            full_url = request.build_absolute_uri(
                reverse("expiring-image", args=[expiring_link])
            )
            instance.expiration_image = full_url

        if not link_to_original_file:
            instance.file = ""
