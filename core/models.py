from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

# Create your models here.

TIERS = (
    ("Basic", "Basic"),
    ("Premium", "Premium"),
    ("Enterprise", "Enterprise"),
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create, save and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model representing user in the system."""

    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    tier = models.CharField(
        max_length=20,
        choices=TIERS,
        default="Basic",
    )
    custom_tier = models.ForeignKey(
        "CustomTier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    objects = UserManager()
    USERNAME_FIELD = "email"


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to="images/")
    expiration_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(30000), MinValueValidator(300)],
    )
    expiration_image = models.CharField(blank=True, null=True, max_length=255)
    thumbnail_200px = models.ImageField(
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg"])],
    )
    thumbnail_400px = models.ImageField(
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg"])],
    )
    custom_thumbnail = models.ImageField(
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg"])],
    )

    def __str__(self):
        return self.file


class CustomTier(models.Model):
    name = models.CharField(max_length=100)
    thumbnail_sizes = models.CharField(max_length=255)
    include_original_link = models.BooleanField(default=False)
    generate_expiring_links = models.BooleanField(default=False)

    def __str__(self):
        return self.name
