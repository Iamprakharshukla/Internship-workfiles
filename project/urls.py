from django.contrib import admin
from django.urls import path, include
from blood_request.views import home_view, staff_dashboard, update_task_status  # Import dashboard views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("portal/", staff_dashboard, name="staff_dashboard"),
    path("portal/task/<int:pk>/update/", update_task_status, name="update_task_status"),
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

        # --- RBAC SETUP (Groups & Permissions) ---
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from blood_request.models import Campaign, Project, Task

        # 1. Create Managers Group
        manager_group, created = Group.objects.get_or_create(name='Managers')
        if created:
            # Managers get full access to core models
            models_to_manage = [Campaign, Project, Task]
            for model in models_to_manage:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(content_type=content_type)
                for perm in permissions:
                    manager_group.permissions.add(perm)
            print("Systems > Group 'Managers' created with full permissions.")

        # 2. Create Staff Group
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            # Staff can View Projects/Campaigns, and View/Change Tasks
            # (In reality, they only change tasks assigned to them, but we need the perm first)
            
            # Read-Only for Campaigns/Projects
            for model in [Campaign, Project]:
                ct = ContentType.objects.get_for_model(model)
                view_perm = Permission.objects.get(content_type=ct, codename=f'view_{model.__name__.lower()}')
                staff_group.permissions.add(view_perm)
            
            # View + Change for Tasks
            task_ct = ContentType.objects.get_for_model(Task)
            task_perms = Permission.objects.filter(content_type=task_ct, codename__in=['view_task', 'change_task'])
            for perm in task_perms:
                staff_group.permissions.add(perm)
                
            print("Systems > Group 'Staff' created with limited permissions.")

        # 3. Create RBAC Demo Users
        if not User.objects.filter(username='manager1').exists():
            u = User.objects.create_user('manager1', 'manager1@example.com', 'pass123')
            u.is_staff = True  # Needed to access Admin/Portal
            u.groups.add(manager_group)
            u.save()
            print("Systems > User 'manager1' created (Role: Manager).")

        if not User.objects.filter(username='staff1').exists():
            u = User.objects.create_user('staff1', 'staff1@example.com', 'pass123')
            u.is_staff = True
            u.groups.add(staff_group)
            u.save()
            print("Systems > User 'staff1' created (Role: Staff).")
            
            # Seed a demo task for staff1
            Task.objects.create(
                title="Prepare Annual Report Draft",
                description="Compile the financial and impact data for the 2024-2025 annual report.",
                assigned_to=u,
                status="To Do",
                priority="High",
                due_date=datetime.date.today() + datetime.timedelta(days=7)
            )
            print("Systems > Assigned Demo Task to 'staff1'.")

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
