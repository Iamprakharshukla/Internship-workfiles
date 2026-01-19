from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from blood_request.models import Campaign, Project, Task
import datetime
import shutil
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Seeds the database with initial data (Roles, Users, Content)'

    def handle(self, *args, **options):
        self.stdout.write("Systems > Starting Seeding Process...")

        # 1. Create Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write("Systems > Superuser 'admin' created.")

        # 2. RBAC SETUP
        # Create Managers Group
        manager_group, created = Group.objects.get_or_create(name='Managers')
        if created:
            models_to_manage = [Campaign, Project, Task]
            for model in models_to_manage:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(content_type=content_type)
                for perm in permissions:
                    manager_group.permissions.add(perm)
            self.stdout.write("Systems > Group 'Managers' created.")

        # Create Staff Group
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            for model in [Campaign, Project]:
                ct = ContentType.objects.get_for_model(model)
                view_perm = Permission.objects.get(content_type=ct, codename=f'view_{model.__name__.lower()}')
                staff_group.permissions.add(view_perm)
            
            task_ct = ContentType.objects.get_for_model(Task)
            task_perms = Permission.objects.filter(content_type=task_ct, codename__in=['view_task', 'change_task'])
            for perm in task_perms:
                staff_group.permissions.add(perm)
            self.stdout.write("Systems > Group 'Staff' created.")

        # 3. Create Demo Users
        if not User.objects.filter(username='manager1').exists():
            u = User.objects.create_user('manager1', 'manager1@example.com', 'pass123')
            u.is_staff = True
            u.groups.add(manager_group)
            u.save()
            self.stdout.write("Systems > User 'manager1' created.")

        if not User.objects.filter(username='staff1').exists():
            u = User.objects.create_user('staff1', 'staff1@example.com', 'pass123')
            u.is_staff = True
            u.groups.add(staff_group)
            u.save()
            
            # Seed Demo Task
            Task.objects.create(
                title="Prepare Annual Report Draft",
                description="Compile the financial and impact data for the 2024-2025 annual report.",
                assigned_to=u,
                status="To Do",
                priority="High",
                due_date=datetime.date.today() + datetime.timedelta(days=7)
            )
            self.stdout.write("Systems > Assigned Demo Task to 'staff1'.")

        # 4. Content Seeding
        def seed_image_data(model_cls, data_list, folder):
            if not model_cls.objects.exists():
                self.stdout.write(f"Systems > Seeding {model_cls.__name__}...")
                for item in data_list:
                    img_name = item.pop('img_filename')
                    static_path = os.path.join(settings.BASE_DIR, 'static', 'assets', img_name)
                    media_path = os.path.join(settings.MEDIA_ROOT, folder, img_name)
                    os.makedirs(os.path.dirname(media_path), exist_ok=True)
                    
                    if not os.path.exists(media_path) and os.path.exists(static_path):
                        shutil.copy(static_path, media_path)
                    
                    obj = model_cls(**item)
                    if os.path.exists(media_path):
                        obj.image.name = f"{folder}/{img_name}"
                    obj.save()

        # Campaigns
        campaigns = [
            {"title": "Appeal For Support: Help Puvendra Singh", "goal_amount": 200000, "raised_amount": 12000, "img_filename": "p1.jpeg", "description": "Help Puvendra Singh..."},
            {"title": "Empower A Single Mother’s Business", "goal_amount": 60000, "raised_amount": 45000, "img_filename": "p2.jpg", "description": "Support a single mother..."},
            {"title": "Support Sachin In Fight Against Cancer", "goal_amount": 100000, "raised_amount": 85000, "img_filename": "p3.jpeg", "description": "Sachin needs your help..."}
        ]
        seed_image_data(Campaign, campaigns, 'campaigns')

        # Projects
        projects = [
            {"title": "Enabling Future Through Youth Skill Development", "description": "Skill Development Centre...", "img_filename": "p4.jpg", "date": datetime.date(2025, 5, 26)},
            {"title": "Shiksha Plus Initiative", "description": "Adult literacy program...", "img_filename": "p5.jpg", "date": datetime.date(2024, 12, 4)},
            {"title": "Shelter Homes Operation", "description": "Urban Homeless scheme...", "img_filename": "p6.webp", "date": datetime.date(2024, 2, 16)}
        ]
        seed_image_data(Project, projects, 'projects')

        self.stdout.write(self.style.SUCCESS("Systems > Seeding Completed Successfully."))
