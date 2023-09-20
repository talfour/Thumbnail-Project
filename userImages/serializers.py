from rest_framework import serializers

from core.models import Image


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for Images"""

    class Meta:
        model = Image
        fields = [
            "file",
            "thumbnail_200px",
            "thumbnail_400px",
            "custom_thumbnail",
            "expiration_time",
            "expiration_image",
        ]
        read_only_fields = (
            "expiration_image",
            "thumbnail_200px",
            "thumbnail_400px",
            "custom_thumbnail",
        )
