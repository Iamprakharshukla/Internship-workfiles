from django.contrib import admin
from .models import BloodDonor, BloodRequest, Report, Campaign, Task, Project

# Register your models here.

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'city', 'phone', 'created_at')
    search_fields = ('name', 'city', 'phone')
    list_filter = ('blood_group', 'city', 'consent_given')

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('contact_person', 'blood_group', 'city', 'units', 'created_at')
    list_filter = ('blood_group', 'city')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'created_at')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_vs_raised', 'created_at')
    
    def target_vs_raised(self, obj):
        return f"{obj.raised_amount} / {obj.goal_amount}"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'due_date', 'updated_at')
    list_filter = ('status', 'assigned_to')
    search_fields = ('title', 'description')

    def save_model(self, request, obj, form, change):
        # check if assigned_to changed or if it's new
        if obj.assigned_to:
            # Simple logic: Send email on assignment (new or changed)
            # In real app, check if 'assigned_to' actually changed
            subject = f"New Task Assigned: {obj.title}"
            message = f"Hello {obj.assigned_to.username},\n\nYou have been assigned a new task:\n\nTitle: {obj.title}\nDescription: {obj.description}\nDue Date: {obj.due_date}\n\nPlease update the status in the dashboard.\n\nRegards,\nAdmin"
            
            # Send email (prints to console)
            print("---------------------------------------------------------")
            print(f"Systems > Sending Email to {obj.assigned_to.email or 'staff@example.com'}...")
            try:
                send_mail(
                    subject,
                    message,
                    'admin@udaansociety.org',
                    [obj.assigned_to.email or 'staff@example.com'],
                    fail_silently=False,
                )
                print("Systems > Email Sent Successfully")
            except Exception as e:
                print(f"Systems > Email Failed: {e}")
            print("---------------------------------------------------------")

        super().save_model(request, obj, form, change)
