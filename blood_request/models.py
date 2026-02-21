from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

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
    last_donation_date = models.DateField(null=True, blank=True)
    donation_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_best_call_time(self):
        """
        Heuristic to suggest best time to call.
        Logic: Metro cities -> Evening (Work hours), Others -> Morning/Afternoon.
        """
        metro_cities = ['Mumbai', 'New Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune']
        
        # Simple string matching
        if any(city.lower() in self.city.lower() for city in metro_cities):
            return "Evening (6:00 PM - 9:00 PM)"
        
        return "Morning (10:00 AM - 1:00 PM)"

    def __str__(self):
        return f"{self.name} ({self.blood_group}) - Score: {self.score}"

class Donation(models.Model):
    donor = models.ForeignKey(BloodDonor, on_delete=models.CASCADE, related_name='donations')
    date = models.DateField()
    units = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation by {self.donor.name} on {self.date}"

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
    # FSM State Management
    from django_fsm import FSMField, transition

    STATUS_RECEIVED = 'Received'
    STATUS_VERIFIED = 'Verified'
    STATUS_FULFILLING = 'Fulfilling'
    STATUS_CLOSED = 'Closed'

    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_FULFILLING, 'Fulfilling'),
        (STATUS_CLOSED, 'Closed'),
    ]

    status = FSMField(default=STATUS_RECEIVED, choices=STATUS_CHOICES, protected=True)

    def __str__(self):
        return f"Request: {self.blood_group} by {self.contact_person} in {self.city} ({self.status})"

    @transition(field=status, source=STATUS_RECEIVED, target=STATUS_VERIFIED)
    def verify(self):
        """Mark the request as verified by staff."""
        pass

    @transition(field=status, source=STATUS_VERIFIED, target=STATUS_FULFILLING)
    def start_fulfilling(self):
        """Start the fulfillment process (finding donors)."""
        pass

    @transition(field=status, source=[STATUS_RECEIVED, STATUS_VERIFIED, STATUS_FULFILLING], target=STATUS_CLOSED)
    def close(self):
        """Close the request (completed or cancelled)."""
        pass

    created_at = models.DateTimeField(auto_now_add=True)

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
    content = CKEditor5Field(blank=True, help_text="Full HTML content for the detail page", config_name='extends')
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

class Testimonial(models.Model):
    text = models.TextField(help_text="The testimonial quote (summary)")
    detailed_text = models.TextField(help_text="Full story/details (shown on expand)", blank=True, null=True)
    author = models.CharField(max_length=100, help_text="Name of the person")
    role = models.CharField(max_length=100, help_text="Role or designation (e.g. Volunteer)")
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} ({self.role})"

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

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No Show', 'No Show'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    
    # Generic Relation (Optional: link to specific donor/project if needed)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    entity = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

class PersonalNote(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_note')
    content = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.user.username}"
class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field(config_name='extends')   # <-- RichTextEditor
    description = models.TextField()
    image = models.ImageField(upload_to='blogs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --- Phase 17: Team Spaces & Knowledge Sharing ---

# --- Phase 22: Workspace Architecture ---

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    members = models.ManyToManyField(User, through='WorkspaceMember', related_name='workspaces')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WorkspaceMember(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Member', 'Member'),
        ('Viewer', 'Viewer'),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workspace', 'user')

class Team(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='teams', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SharedNote(models.Model):
    title = models.CharField(max_length=200, default="Untitled Note")
    content = CKEditor5Field(config_name='extends', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_with_teams = models.ManyToManyField(Team, related_name='shared_notes', blank=True)
    shared_with_users = models.ManyToManyField(User, related_name='received_notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class CampusAmbassador(models.Model):

    name = models.CharField(max_length=200)

    college = models.CharField(max_length=200)

    city = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="ambassadors/",
        blank=True,
        null=True
    )

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class NewsClipping(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news_clippings/')
    newspaper = models.CharField(max_length=100)
    date_display = models.CharField(max_length=50, help_text="e.g. June 2026")
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

