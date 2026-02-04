import os
from django.db import migrations
from django.conf import settings

def populate_blogs(apps, schema_editor):
    Blog = apps.get_model('blood_request', 'Blog')
    blogs_dir = os.path.join(settings.MEDIA_ROOT, 'blogs')
    
    if not os.path.exists(blogs_dir):
        return

    # Filter out duplicates and thumbnails (usually have _hash in name)
    # Simple logic: iterate all files.
    for filename in os.listdir(blogs_dir):
        if not os.path.isfile(os.path.join(blogs_dir, filename)):
            continue
            
        # simple check for image extension
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue

        relative_path = f"blogs/{filename}"
        
        # Check if already exists to avoid duplicates on re-run
        if Blog.objects.filter(image=relative_path).exists():
            continue

        # Create title from filename
        # Remove extension
        title_raw = os.path.splitext(filename)[0]
        # Replace hyphens/underscores with spaces
        title_clean = title_raw.replace('-', ' ').replace('_', ' ')
        # Capitalize
        title = title_clean.title()
        
        # Placeholder description
        description = f"This is a blog post about {title}. Read more to explore our initiatives."

        Blog.objects.create(
            title=title,
            description=description,
            image=relative_path
        )

class Migration(migrations.Migration):

    dependencies = [
        ('blood_request', '0014_merge_20260204_0037'), # Auto-detects previous migration usually, but explicit dependency helps
    ]

    operations = [
        migrations.RunPython(populate_blogs),
    ]
