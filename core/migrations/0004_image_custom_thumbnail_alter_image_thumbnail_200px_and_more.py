# Generated by Django 4.2.5 on 2023-09-20 11:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_user_custom_tier'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='custom_thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg'])]),
        ),
        migrations.AlterField(
            model_name='image',
            name='thumbnail_200px',
            field=models.ImageField(blank=True, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg'])]),
        ),
        migrations.AlterField(
            model_name='image',
            name='thumbnail_400px',
            field=models.ImageField(blank=True, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg'])]),
        ),
    ]