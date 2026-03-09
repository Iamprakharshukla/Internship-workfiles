from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PolicyReport

from .models import (
    BloodDonor, BloodRequest, Campaign, Report, Project, Task, SubTask,
    Announcement, Testimonial, StaffProfile, Interaction, Appointment,
    PersonalNote, Team, SharedNote, NewsClipping, Blog, Expense, ContactMessage
)

@admin.register(PolicyReport)
class PolicyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    list_filter = ('category',)
    search_fields = ('title',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'created_at')
    search_fields = ('title',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role', 'is_active', 'created_at')
    list_filter = ('is_active',)


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

from .models import Interaction
@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('staff', 'interaction_type', 'outcome', 'next_followup_date', 'created_at')
    list_filter = ('staff', 'interaction_type', 'outcome')
    search_fields = ('notes',)

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'city', 'phone', 'score', 'donation_count')
    search_fields = ('name', 'city', 'phone')
    list_filter = ('blood_group', 'city', 'consent_given')
    readonly_fields = ('score', 'donation_count')

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('contact_person', 'blood_group', 'city', 'units', 'status', 'created_at')
    list_filter = ('blood_group', 'city', 'status')
    readonly_fields = ('status',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_vs_raised', 'created_at')
    
    def target_vs_raised(self, obj):
        return f"{obj.raised_amount} / {obj.goal_amount}"

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'category', 'campaign', 'logged_by')
    list_filter = ('category', 'date', 'campaign')
    search_fields = ('title', 'notes')

# Note: Internal workspace tools (Project, Task, SubTask, Team, SharedNote) 
# have been explicitly removed from the Admin panel and migrated to the UDAAN Portal 
# for a unified Notion-like workspace experience.



from .models import CampusAmbassador, CampusAmbassadorApplication

@admin.register(CampusAmbassador)
class CampusAmbassadorAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'city', 'created_at')
    search_fields = ('name', 'college')

@admin.register(CampusAmbassadorApplication)
class CampusAmbassadorApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'college', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('full_name', 'college', 'email')

@admin.register(NewsClipping)
class NewsClippingAdmin(admin.ModelAdmin):
    list_display = ('title', 'newspaper', 'date_display', 'created_at')
    search_fields = ('title', 'newspaper')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('first_name', 'email', 'subject')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"

from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active', 'created_at')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'description')
