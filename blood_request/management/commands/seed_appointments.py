from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blood_request.models import Appointment
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with demo appointments'

    def handle(self, *args, **kwargs):
        staff_users = User.objects.filter(is_staff=False, is_superuser=False)
        
        if not staff_users.exists():
            self.stdout.write(self.style.WARNING("No staff users found. Creating 'staff1'..."))
            staff1 = User.objects.create_user('staff1', 'staff1@example.com', 'password123')
            staff_users = [staff1]
        
        titles = [
            "Donor Follow-up: John Doe",
            "Site Visit: Aligarh Center",
            "Team Sync: Weekly",
            "Equipment Check",
            "Camp Planning Meeting"
        ]
        
        statuses = ['Scheduled', 'Completed', 'Cancelled']
        
        count = 0
        for user in staff_users:
            for _ in range(3): # Create 3 appointments per staff
                base_time = timezone.now() + timedelta(days=random.randint(-2, 5))
                Appointment.objects.create(
                    title=random.choice(titles),
                    description="This is a demo appointment generated for testing.",
                    start_time=base_time,
                    end_time=base_time + timedelta(hours=1),
                    staff=user,
                    status=random.choice(statuses)
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} demo appointments.'))
