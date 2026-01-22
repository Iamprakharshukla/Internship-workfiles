from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import BloodDonor, BloodRequest, Report, Campaign, Task, Project, SubTask, Announcement, StaffProfile

# Define an inline admin descriptor for StaffProfile model
class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile (Phone)'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (StaffProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')
    
    def get_phone(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Phone Number'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_task', 'status', 'assigned_to')
    list_filter = ('status',)

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
    filter_horizontal = ('managers',) # Better UI for ManyToMany

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_vs_raised', 'created_at')
    
    def target_vs_raised(self, obj):
        return f"{obj.raised_amount} / {obj.goal_amount}"

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'project', 'assigned_to')
    search_fields = ('title', 'description')
    inlines = [SubTaskInline]
    
    # Note: Email logic moved to signals.py in Phase 5
