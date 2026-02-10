import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import BloodDonor, BloodRequest
from .schemas import DonorSchema
from pydantic import ValidationError
# from django.shortcuts import render
from .models import Blog, Project
from django.shortcuts import get_object_or_404

@ensure_csrf_cookie
def index(request):
    """
    Renders the main page. CSRF cookie is ensured for AJAX requests.
    """
    return render(request, 'blood_request/index.html')

def register_donor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 1. Validate with Pydantic
            donor_data = DonorSchema(**data)
            
            # 2. Check logic unique phone (Pydantic doesn't check DB)
            if BloodDonor.objects.filter(phone=donor_data.phone).exists():
                return JsonResponse({'success': False, 'error': 'Phone number already registered.'}, status=400)

            # 3. Create Model Instance
            donor = BloodDonor.objects.create(
                name=donor_data.name,
                blood_group=donor_data.blood_group,
                phone=donor_data.phone,
                email=donor_data.email,
                city=donor_data.city,
                state=donor_data.state,
                pin_code=donor_data.pin_code,
                consent_given=donor_data.consent_given
            )
            return JsonResponse({'success': True, 'message': 'Registration successful!'})

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

def search_donors(request):
    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')

    donors = BloodDonor.objects.all()

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    
    if city:
        donors = donors.filter(city__icontains=city)
    
    results = []
    for donor in donors:
        results.append({
            'name': donor.name,
            'blood_group': donor.blood_group,
            'phone': donor.phone, # In a real app, might want to mask this or show only on request
            'email': donor.email,
            'city': donor.city,
            'state': donor.state
        })

    return JsonResponse({'results': results})

def blood_request_create(request):
    if request.method == "POST":
        try:
            # Handle standard form data
            data = json.loads(request.body)
            
            # Simple validation for required fields
            required_fields = ['city', 'pin_code', 'blood_group', 'units', 'address_line_2', 'contact_person', 'contact_phone']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"success": False, "error": f"{field.replace('_', ' ').title()} is required."}, status=400)

            blood_request = BloodRequest.objects.create(
                city=data.get('city'),
                pin_code=data.get('pin_code'),
                blood_group=data.get('blood_group'),
                units=int(data.get('units')),
                address_line_1=data.get('address_line_1', ''),
                address_line_2=data.get('address_line_2'),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                # File handling omitted for JSON payload simplicity in this step
            )
            return JsonResponse({"success": True, "message": "Blood request submitted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

from .models import Campaign, Report, Project

def home_view(request):
    """
    Renders the homepage with dynamic content.
    """
    campaigns = Campaign.objects.all().order_by('-created_at')[:3]
    projects = Project.objects.all().order_by('-date')[:3]
    # Keep Reports if needed, or remove if Projects replaces it entirely. 
    # The user asked to replace "Projects" section which was static.
    
    context = {
        'campaigns': campaigns,
        'projects': projects
    }
    return render(request, 'home.html', context)

from django.contrib.auth.decorators import login_required
from .models import Task

@login_required
def staff_dashboard(request):
    """
    Staff Dashboard: Kanban Board View with Bulletin and Task Grouping.
    """
    from .models import Announcement, BloodDonor
    
    # Fetch Active Announcements
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    # Impact Stats
    total_donors = BloodDonor.objects.count()

    # Fetch all tasks for the user
    all_tasks = Task.objects.filter(assigned_to=request.user).order_by('due_date')
    
    # Simple Python-side grouping (efficient enough for <100 tasks)
    todo_tasks = [t for t in all_tasks if t.status == 'To Do']
    inprogress_tasks = [t for t in all_tasks if t.status == 'In Progress']
    done_tasks = [t for t in all_tasks if t.status == 'Done']

    context = {
        'announcements': announcements,
        'total_donors': total_donors,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
    }
    return render(request, 'staff_dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_task_status(request, pk):
    from django.utils import timezone
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    # Get GPS data if provided
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')

    # Simple Toggle for now: To Do -> In Progress -> Done -> To Do
    if task.status == 'To Do':
        task.status = 'In Progress'
    elif task.status == 'In Progress':
        task.status = 'Done'
        # Only save completion data when marking as Done
        if lat and lng:
            task.completion_lat = lat
            task.completion_lng = lng
        task.completion_timestamp = timezone.now()
    else:
        task.status = 'To Do'
        # specific logic for re-opening? maybe clear completion data?
        # for now, keep history.
        
    task.save()
    return redirect('staff_dashboard')

from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Managers').exists()

@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Manager Dashboard: View ALL tasks across the organization.
    Enhanced with Phase 7 metrics: Progress Bars, Resource Load, Bottlenecks.
    """
    from django.db.models import Count, Q
    from django.contrib.auth.models import User
    from datetime import date
    
    # 1. Task Overview
    tasks = Task.objects.all().order_by('status', '-created_at')
    
    # 2. Project Progress (Phase 7.1)
    # Calculate % completion for each project
    projects = Project.objects.annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='Done'))
    ).filter(total_tasks__gt=0) # Only show projects with tasks
    
    # Attach percentage manually (Django annotations for division can be complex database-dependent)
    for p in projects:
        if p.total_tasks > 0:
            p.progress = int((p.completed_tasks / p.total_tasks) * 100)
        else:
            p.progress = 0

    # 3. Resource Allocation (Phase 7.2)
    # Count open tasks (Not Done) for each staff member
    staff_load = User.objects.filter(is_staff=False, is_superuser=False).annotate(
        active_task_count=Count('tasks', filter=~Q(tasks__status='Done'))
    ).order_by('-active_task_count')

    # 4. Bottlenecks (Phase 7.3)
    # Tasks that are NOT Done and Past Due date
    overdue_tasks = Task.objects.filter(
        ~Q(status='Done'),
        due_date__lt=date.today()
    ).order_by('due_date')

    # Simple stats
    stats = {
        'total': tasks.count(),
        'high_priority': tasks.filter(priority__in=['High', 'Critical']).count(),
        'pending': tasks.filter(status__in=['To Do', 'In Progress']).count(),
        'overdue': overdue_tasks.count()
    }

    context = {
        'tasks': tasks,
        'stats': stats,
        'projects': projects,
        'staff_load': staff_load,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'manager_dashboard.html', context)

def campaign_list(request):
    """
    Public Campaign Listing Page
    """
    campaigns = Campaign.objects.all().order_by('-created_at')
    return render(request, 'campaigns.html', {'campaigns': campaigns})

def project_list(request):
    """
    Public Project Listing Page
    """
    projects = Project.objects.all().order_by('-date')
    return render(request, 'projects.html', {'projects': projects})

def project_detail(request, slug):
    """
    Specific Project Detail Page
    """
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'project_detail.html', {'project': project})

def blogs_page(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs})


def projects_page(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': projects})

def report_list(request):

    return render(request, 'annual_reports.html')

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    recent_blogs = Blog.objects.exclude(id=id).order_by('-created_at')[:4]

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'recent_blogs': recent_blogs
    })

    return render(request, 'annual_reports.html', {'reports': reports})



def locations(request):
    return render(request, 'locations.html')

from django.contrib.contenttypes.models import ContentType
from .models import Interaction

@login_required
def donor_detail(request, pk):
    
    donor = get_object_or_404(BloodDonor, pk=pk)
    
    # Handle New Interaction Log
    if request.method == 'POST':
        interaction_type = request.POST.get('interaction_type')
        outcome = request.POST.get('outcome')
        notes = request.POST.get('notes')
        followup_date = request.POST.get('next_followup_date') or None
        
        # Create Interaction linked to this Donor
        Interaction.objects.create(
            staff=request.user,
            content_type=ContentType.objects.get_for_model(BloodDonor),
            object_id=donor.id,
            interaction_type=interaction_type,
            outcome=outcome,
            notes=notes,
            next_followup_date=followup_date
        )
        return redirect('donor_detail', pk=pk)
    
    # Fetch Interaction History
    ct = ContentType.objects.get_for_model(BloodDonor)
    interactions = Interaction.objects.filter(
        content_type=ct, 
        object_id=donor.id
    ).order_by('-created_at')

    return render(request, 'blood_request/donor_detail.html', {
        'donor': donor,
        'interactions': interactions,
        'interaction_types': Interaction.INTERACTION_TYPES,
    })


def career_fellowship(request):
    return render(request, 'career_and_fellowship.html')

# --- Appointment Scheduling (Phase 8) ---
from .models import Appointment, PersonalNote
from django.http import JsonResponse

@login_required
def personal_notes_api(request):
    """API to get/save personal notes"""
    # Use get_or_create to ensure a note exists
    note, created = PersonalNote.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            note.content = data.get('content', '')
            note.save()
            return JsonResponse({'status': 'saved', 'updated_at': note.updated_at})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'content': note.content, 'updated_at': note.updated_at})

@login_required
def appointment_list(request):
    # Show user's appointments
    appointments = Appointment.objects.filter(staff=request.user).order_by('start_time')
    return render(request, 'appointments.html', {'appointments': appointments})

@login_required
def appointment_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')
        description = request.POST.get('description')
        
        if title and start and end:
            Appointment.objects.create(
                title=title,
                start_time=start,
                end_time=end,
                description=description,
                staff=request.user,
                status='Scheduled'
            )
            return redirect('appointment_list')
    
    return render(request, 'appointment_form.html')


