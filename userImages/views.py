import os

from django.conf import settings
from django.core import signing
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Image

from .image_processors import (
    BasicImageProcessor,
    CustomImageProcessor,
    EnterpriseImageProcessor,
    PremiumImageProcessor,
)
from .serializers import ImageSerializer


class ImageUploadView(viewsets.ModelViewSet):
    """
    Viewset for handling image uploads and managing image data.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    def get_queryset(self):
        """
        Filters the queryset based on the user.
        If the user is not logged in, it returns a response with an error message.
        """
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(user=user)
        user_tier = user.tier
        custom_user_tier = user.custom_tier
        if custom_user_tier is not None:
            CustomImageProcessor().process_image(
                instance, custom_user_tier, self.request
            )
        else:
            if user_tier == "Basic":
                BasicImageProcessor().process_image(instance)
                instance.file = ""
            elif user_tier == "Premium":
                BasicImageProcessor().process_image(instance)
                PremiumImageProcessor().process_image(instance)
            elif user_tier == "Enterprise":
                BasicImageProcessor().process_image(instance)
                PremiumImageProcessor().process_image(instance)
                EnterpriseImageProcessor().process_image(instance, self.request)

        instance.save()


class ExpiringImageView(APIView):
    """View for handling expiring image upload."""

    def get(self, request, signed_data):
        """Get the image from the signed data."""
        try:
            # Verify the signed data and extract the URL and expiration time
            url, expiration_time_str = signing.loads(signed_data)
            expiration_time = timezone.datetime.strptime(
                expiration_time_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            # Ensure that timezone.now() is in the same timezone as expiration_time
            now = timezone.now()
            now = now.replace(tzinfo=expiration_time.tzinfo)

            if now > expiration_time:
                return Response({"message": "Link has expired."}, status=404)

            # Remove any leading '/' from the URL and join it with MEDIA_ROOT
            full_path = os.path.join(settings.MEDIA_ROOT, url).lstrip("/")

            if not os.path.isfile(full_path):
                return Response({"message": "File not found."}, status=404)

            with open(full_path, "rb") as image_file:
                response = HttpResponse(image_file, content_type="image/png")

            return response

        except signing.BadSignature:
            raise Response({"message": "Invalid or expired link."})
