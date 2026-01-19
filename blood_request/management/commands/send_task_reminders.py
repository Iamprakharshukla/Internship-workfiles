from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from blood_request.models import Task
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends daily email reminders for due and overdue tasks'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.stdout.write(f"Running Task Reminders for date: {today}")
        
        # 1. Tasks Due Today
        due_today = Task.objects.filter(due_date=today).exclude(status='Done')
        
        count_due = 0
        for task in due_today:
            if task.assigned_to and task.assigned_to.email:
                subject = f"Reminder: Task Due Today - {task.title}"
                message = (
                    f"Hello {task.assigned_to.username},\n\n"
                    f"This is a reminder that the following task is due today:\n\n"
                    f"Task: {task.title}\n"
                    f"Priority: {task.priority}\n"
                    f"Status: {task.status}\n\n"
                    f"Please update the status in the portal."
                )
                
                self.stdout.write(f" > Sending Due Reminder to {task.assigned_to.email}...")
                send_mail(
                    subject, 
                    message, 
                    settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org', 
                    [task.assigned_to.email],
                    fail_silently=False
                )
                count_due += 1
        
        # 2. Overdue Tasks
        overdue = Task.objects.filter(due_date__lt=today).exclude(status='Done')
        
        count_overdue = 0
        for task in overdue:
             if task.assigned_to and task.assigned_to.email:
                subject = f"URGENT: Task Overdue - {task.title}"
                message = (
                    f"Hello {task.assigned_to.username},\n\n"
                    f"This task is now OVERDUE.\n\n"
                    f"Task: {task.title}\n"
                    f"Due Date: {task.due_date}\n"
                    f"Priority: {task.priority}\n\n"
                    f"Please address this immediately."
                )
                
                self.stdout.write(f" > Sending OVERDUE Warning to {task.assigned_to.email}...")
                send_mail(
                    subject, 
                    message, 
                    settings.DEFAULT_FROM_EMAIL or 'admin@udaan.org', 
                    [task.assigned_to.email],
                    fail_silently=False
                )
                count_overdue += 1

        self.stdout.write(self.style.SUCCESS(f'Done. Sent {count_due} due reminders and {count_overdue} overdue warnings.'))
