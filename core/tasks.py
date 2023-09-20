from celery import shared_task
from PIL import Image


@shared_task()
def create_thumbnail(image_path, thumbnail_path, height=200):
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if the image is in RGBA mode
            if img.mode == "RGBA":
                img = img.convert("RGB")
            width_percent = height / float(img.size[1])
            new_width = int((float(img.size[0]) * float(width_percent)))

            # Resize the image to the new dimensions
            img.thumbnail((new_width, height), Image.Resampling.LANCZOS)

            img.save(thumbnail_path)
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
