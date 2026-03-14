import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser and setup initial configurations for production'

    def handle(self, *args, **kwargs):
        email = 'mail@udaansociety.org'
        username = 'admin'
        password = 'udaanpassword123'  # A default temporary password

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser {username} ({email}) already exists.'))
            return

        self.stdout.write('Creating superuser...')
        user = User.objects.create_superuser(username=username, email=email, password=password)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser!'))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Temporary Password: {password}'))
        self.stdout.write(self.style.SUCCESS(f'\nIMPORTANT: Please log in to the admin panel and use the "Change Password" feature immediately!'))
