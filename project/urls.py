from django.contrib import admin
from django.urls import path, include
from blood_request.views import home_view  # Import the new view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),  # Use home_view
    path("blood-request/", include("blood_request.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# AUTOMATICALLY APPLY MIGRATIONS FOR IN-MEMORY DATABASE
# This workaround ensures tables exist when using :memory: to avoid locking issues.
from django.conf import settings
from django.core.management import call_command
import sys

# We check for 'runserver' to ensure we only run this when the server starts,
# and we catch all errors to prevent crashes if it runs multiple times.
if settings.DEBUG and settings.DATABASES['default']['NAME'] == ':memory:' and 'runserver' in sys.argv:
    try:
        call_command('migrate', interactive=False)
        
        # Auto-Create Users
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            print("Systems > Superuser 'admin' created.")
            
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user('staff', 'staff@example.com', 'staff123')
            staff.is_staff = True
            staff.save()
            print("Systems > Staff user 'staff' created.")

        # Auto-Create Initial Data (Seeding)
        from blood_request.models import Campaign, Project
        import datetime
        import shutil
        import os
        from django.conf import settings

        def seed_image_data(model_cls, data_list, folder):
            if not model_cls.objects.exists():
                print(f"Systems > Seeding {model_cls.__name__}...")
                for item in data_list:
                    # Prepare paths
                    img_name = item.pop('img_filename')
                    static_path = os.path.join(settings.BASE_DIR, 'static', 'assets', img_name)
                    media_path = os.path.join(settings.MEDIA_ROOT, folder, img_name)
                    
                    # Ensure media folder exists
                    os.makedirs(os.path.dirname(media_path), exist_ok=True)
                    
                    # Copy only if missing
                    if not os.path.exists(media_path) and os.path.exists(static_path):
                        shutil.copy(static_path, media_path)
                    
                    # Create object
                    obj = model_cls(**item)
                    
                    # Set image path if valid
                    if os.path.exists(media_path):
                        obj.image.name = f"{folder}/{img_name}"
                    
                    obj.save()
                    print(f"Systems > Created {model_cls.__name__}: {item.get('title')}")

        # Campaigns Data
        campaigns = [
            {
                "title": "Appeal For Support: Help Puvendra Singh",
                "goal_amount": 200000,
                "raised_amount": 12000,
                "img_filename": "p1.jpeg",
                "description": "Help Puvendra Singh in his fight against critical illness."
            },
            {
                "title": "Empower A Single Mother’s Business",
                "goal_amount": 60000,
                "raised_amount": 45000,
                "img_filename": "p2.jpg",
                "description": "Support a single mother to establish her livelihood and support her family."
            },
            {
                "title": "Support Sachin In Fight Against Cancer",
                "goal_amount": 100000,
                "raised_amount": 85000,
                "img_filename": "p3.jpeg",
                "description": "Sachin needs your help to afford life-saving treatment."
            }
        ]
        seed_image_data(Campaign, campaigns, 'campaigns')

        # Projects Data
        projects = [
            {
                "title": "Enabling Future Through Youth Skill Development",
                "description": "UDAAN Society Joins Hands with Bandhan Skill Development Centre for Youth Empowerment.",
                "img_filename": "p4.jpg",
                "date": datetime.date(2025, 5, 26)
            },
            {
                "title": "Shiksha Plus Initiative With Shiv Nadar Foundation",
                "description": "The Shiksha Plus initiative is a program by the Shiv Nadar Foundation focused on adult literacy.",
                "img_filename": "p5.jpg",
                "date": datetime.date(2024, 12, 4)
            },
            {
                "title": "Operation And Management Of Shelter Homes",
                "description": "The shelter homes are constructed under the central government’s Shelter for Urban Homeless scheme.",
                "img_filename": "p6.webp",
                "date": datetime.date(2024, 2, 16)
            }
        ]
        seed_image_data(Project, projects, 'projects')

    except Exception as e:
        print(f"Systems > Initialization Error: {e}")
        pass
