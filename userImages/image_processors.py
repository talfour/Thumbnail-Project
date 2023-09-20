import os

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from core.tasks import create_thumbnail

from .utils import generate_expiring_link


class BasicImageProcessor:
    def process_image(self, instance):
        image_path = instance.file.path
        thumbnail_filename = (
            os.path.splitext(os.path.basename(image_path))[0] + "_thumbnail_200px.jpg"
        )
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "images", thumbnail_filename)

        create_thumbnail.delay(image_path, thumbnail_path)
        instance.thumbnail_200px = os.path.relpath(
            thumbnail_path, start=settings.MEDIA_ROOT
        )


class PremiumImageProcessor:
    def process_image(self, instance):
        image_path = instance.file.path
        thumbnail_filename = (
            os.path.splitext(os.path.basename(image_path))[0] + "_thumbnail_400px.jpg"
        )
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "images", thumbnail_filename)

        create_thumbnail.delay(image_path, thumbnail_path, 400)
        instance.thumbnail_400px = os.path.relpath(
            thumbnail_path, start=settings.MEDIA_ROOT
        )


class EnterpriseImageProcessor:
    def process_image(self, instance, request):
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


class CustomImageProcessor:
    def process_image(self, instance, user_tier, request):
        thumbnail_size = int(user_tier.thumbnail_sizes)
        image_path = instance.file.path
        thumbnail_filename = (
            os.path.splitext(os.path.basename(image_path))[0]
            + f"_thumbnail_{thumbnail_size}px.jpg"
        )
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "images", thumbnail_filename)

        create_thumbnail.delay(image_path, thumbnail_path, thumbnail_size)
        instance.custom_thumbnail = os.path.relpath(
            thumbnail_path, start=settings.MEDIA_ROOT
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
