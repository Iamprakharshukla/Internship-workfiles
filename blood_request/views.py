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
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    # Simple Toggle for now: To Do -> In Progress -> Done -> To Do
    if task.status == 'To Do':
        task.status = 'In Progress'
    elif task.status == 'In Progress':
        task.status = 'Done'
    else:
        task.status = 'To Do'
        
    task.save()
    task.save()
    return redirect('staff_dashboard')

from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Managers').exists()

@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Manager Dashboard: View ALL tasks across the organization.
    """
    # Order by Priority (Critical first)
    # Since priority is text, we might want custom sorting, but simple string sort
    # works if Critical > High > Low... wait C > H > L. Alphabetical is C, H, L, M. 
    # Critical should be top.
    # Ideally we use an IntegerField for sorting, but for now we'll just fetch all.
    tasks = Task.objects.all().order_by('status', '-created_at') 
    
    # Simple stats
    stats = {
        'total': tasks.count(),
        'high_priority': tasks.filter(priority__in=['High', 'Critical']).count(),
        'pending': tasks.filter(status__in=['To Do', 'In Progress']).count()
    }

    context = {
        'tasks': tasks,
        'stats': stats
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
    reports = Report.objects.all().order_by('-published_date')
    return render(request, 'annual_reports.html', {'reports': reports})
