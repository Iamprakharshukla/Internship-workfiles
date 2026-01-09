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

        # Auto-Create Initial Campaigns (Seeding Data)
        from blood_request.models import Campaign
        from django.core.files import File
        from django.conf import settings
        import os
        
        if not Campaign.objects.exists():
            print("Systems > Seeding Initial Campaigns...")
            
            # Helper to get static file
            def get_static_image(filename):
                path = os.path.join(settings.BASE_DIR, 'static', 'assets', filename)
                if os.path.exists(path):
                    return open(path, 'rb')
                return None

            campaigns_data = [
                {
                    "title": "Appeal For Support: Help Puvendra Singh",
                    "goal": 200000,
                    "raised": 12000,
                    "img": "p1.jpeg",
                    "desc": "Help Puvendra Singh in his fight against critical illness."
                },
                {
                    "title": "Empower A Single Mother’s Business",
                    "goal": 60000,
                    "raised": 45000,
                    "img": "p2.jpg",
                    "desc": "Support a single mother to establish her livelihood and support her family."
                },
                {
                    "title": "Support Sachin In Fight Against Cancer",
                    "goal": 100000,
                    "raised": 85000,
                    "img": "p3.jpeg",
                    "desc": "Sachin needs your help to afford life-saving treatment."
                }
            ]
            
            for c in campaigns_data:
                img_file = get_static_image(c['img'])
                if img_file:
                    camp = Campaign(
                        title=c['title'],
                        description=c['desc'],
                        goal_amount=c['goal'],
                        raised_amount=c['raised']
                    )
                    camp.image.save(c['img'], File(img_file), save=True)
                    img_file.close()
                    print(f"Systems > Created Campaign: {c['title']}")

    except Exception as e:
        print(f"Systems > Initialization Error: {e}")
        pass
