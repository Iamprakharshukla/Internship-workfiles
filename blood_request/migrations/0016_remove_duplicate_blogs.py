from django.db import migrations
from django.db.models import Count

def remove_duplicates(apps, schema_editor):
    Blog = apps.get_model('blood_request', 'Blog')
    
    # Find titles that have duplicates
    duplicates = Blog.objects.values('title').annotate(count=Count('id')).filter(count__gt=1)
    
    for duplicate in duplicates:
        title = duplicate['title']
        # Get all blogs with this title, ordered by creation (keep oldest or newest? usually keep oldest/first)
        blogs = Blog.objects.filter(title=title).order_by('id')
        
        # Keep the first one, delete the rest
        if blogs.exists():
            to_delete = blogs[1:]
            for blog in to_delete:
                blog.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('blood_request', '0015_populate_blogs'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates),
    ]
