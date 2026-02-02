from django.db import models
from django.contrib.auth.models import User

class BloodDonor(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    phone = models.CharField(max_length=15, unique=True, help_text="Phone number with country code")
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    consent_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.blood_group}) - {self.city}"

class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    units = models.IntegerField(help_text="Number of units/bags")
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    # Using specific path (though for in-memory/temp usage, plain FileField is fine)
    request_form_file = models.FileField(upload_to='requests/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request: {self.blood_group} by {self.contact_person} in {self.city}"

# --- CMS Models ---
class Report(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='reports/')
    published_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='campaigns/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True) # Will populate via migration
    description = models.TextField(help_text="Short excerpt for the card")
    content = models.TextField(blank=True, help_text="Full HTML content for the detail page")
    image = models.ImageField(upload_to='projects/')
    date = models.DateField()
    managers = models.ManyToManyField(User, related_name='managed_projects', blank=True, help_text="Managers responsible for this project")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --- Project Management Models ---
from django.contrib.auth.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    remarks = models.TextField(blank=True, help_text="Staff notes or completion comments")
    due_date = models.DateField(null=True, blank=True)
    
    # GPS Tagging (Phase 9)
    completion_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    completion_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    completion_timestamp = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.priority}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --- NGO Suite: Enhanced Data Structures (Phase 6) ---

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Contact number for urgent coordination")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class SubTask(models.Model):
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    ]
    
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sub: {self.title} ({self.status})"

# --- CRM & Interactions (Phase 8) ---

# --- CRM & Interactions (Phase 8) ---
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Interaction(models.Model):
    INTERACTION_TYPES = [
        ('Call', 'Call'),
        ('Meeting', 'Meeting'),
        ('Email', 'Email'),
        ('Visit', 'Visit'),
    ]
    
    OUTCOME_CHOICES = [
        ('Interested', 'Interested'),
        ('Follow-up Scheduled', 'Follow-up Scheduled'),
        ('Closed', 'Closed'),
        ('Not Interested', 'Not Interested'),
    ]

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    
    # Generic Relation (Can link to BloodDonor, BloodRequest, Project, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES, default='Interested')
    notes = models.TextField(blank=True)
    next_followup_date = models.DateField(null=True, blank=True, help_text="If set, a task will be auto-created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interaction_type} by {self.staff.username} ({self.outcome})"
class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='blogs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title