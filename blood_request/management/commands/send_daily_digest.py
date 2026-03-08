from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from blood_request.models import Task
from django.conf import settings
from datetime import date

class Command(BaseCommand):
    help = 'Sends a daily digest of pending and in-progress tasks to staff members'

    def handle(self, *args, **kwargs):
        # We only want to send digest to active users who belong to Staff or Managers
        staff_users = User.objects.filter(is_active=True, is_staff=True)
        
        emails_sent = 0
        
        for user in staff_users:
            if not user.email:
                continue
                
            tasks = Task.objects.filter(
                assigned_to=user,
                status__in=['To Do', 'In Progress']
            ).order_by('due_date', '-priority')
            
            if not tasks.exists():
                # Don't send an email if they have 0 active tasks
                continue
                
            # Render HTML template 
            html_message = render_to_string(
                'blood_request/emails/daily_digest.html',
                {
                    'user': user,
                    'tasks': tasks,
                    'today': date.today()
                }
            )
            
            # Plain text fallback
            plain_message = f"Hello {user.first_name or user.username},\n\nYou have {tasks.count()} pending tasks today.\nPlease log in to the portal to view them."
            
            try:
                send_mail(
                    subject=f"UDAAN Tasks Daily Digest - {date.today().strftime('%b %d, %Y')}",
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                emails_sent += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully sent digest to {user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send digest to {user.username}: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS(f'Finished sending {emails_sent} daily digests.'))
