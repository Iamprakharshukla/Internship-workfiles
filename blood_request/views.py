import json
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import BloodDonor, BloodRequest
from .schemas import DonorSchema
from pydantic import ValidationError
# from django.shortcuts import render
from .models import Blog, Project, Task
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
    from .models import Testimonial
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:7]
    
    context = {
        'campaigns': campaigns,
        'projects': projects,
        'testimonials': testimonials
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

    # Recent Activity (Last 5 updated tasks)
    recent_activity = Task.objects.filter(assigned_to=request.user).order_by('-updated_at')[:5]

    context = {
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'announcements': announcements,
        'total_donors': total_donors,
        'recent_activity': recent_activity,
    }
    return render(request, 'staff_dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_task_status(request, pk):
    from django.utils import timezone
    import json
    
    # Check if this is an AJAX/JSON request
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    new_status = None
    
    if is_ajax:
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            # GPS data from AJAX
            lat = data.get('lat')
            lng = data.get('lng')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        # Form submission
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')

    # Logic
    if new_status:
        # Direct status update (Drag & Drop)
        if new_status in ['To Do', 'In Progress', 'Done']:
            task.status = new_status
            if new_status == 'Done':
                task.completion_timestamp = timezone.now()
                if lat and lng:
                    task.completion_lat = lat
                    task.completion_lng = lng
    else:
        # Toggle logic (Legacy/Button)
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
        
    task.save()
    
    if is_ajax:
        return JsonResponse({'status': 'success', 'new_status': task.status, 'task_id': task.pk})
    
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
    all_tasks = Task.objects.all().order_by('-created_at')
    
    # Kanban Buckets
    todo_tasks = all_tasks.filter(status='To Do')
    inprogress_tasks = all_tasks.filter(status='In Progress')
    done_tasks = all_tasks.filter(status='Done')
    
    tasks = all_tasks # Keep for table if needed or backward compat
    
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
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
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

def resources_page(request):
    """Render the resources page"""
    return render(request, "resources.html")

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


@login_required
def profile_edit(request):
    from .forms import UserUpdateForm, ProfileUpdateForm
    from .models import StaffProfile

    # Ensure StaffProfile exists
    profile, created = StaffProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            from django.contrib import messages
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_edit')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'profile.html', context)

# --- Phase 16: Data Export Suite ---
import csv
from django.http import HttpResponse

@user_passes_test(is_manager)
def export_donors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blood_donors.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Blood Group', 'City', 'Phone', 'Email', 'Last Donation', 'Donation Count', 'Score'])

    donors = BloodDonor.objects.all().values_list(
        'name', 'blood_group', 'city', 'phone', 'email', 'last_donation_date', 'donation_count', 'score'
    )
    for donor in donors:
        writer.writerow(donor)

    return response

@user_passes_test(is_manager)
def export_requests_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blood_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['Contact Person', 'Phone', 'City', 'Blood Group', 'Units', 'Status', 'Created At'])

    requests = BloodRequest.objects.all().values_list(
        'contact_person', 'contact_phone', 'city', 'blood_group', 'units', 'status', 'created_at'
    )
    for req in requests:
        writer.writerow(req)

    return response

@login_required
def calendar_events_api(request):
    """API for FullCalendar"""
    events = []
    
    # Tasks
    tasks = Task.objects.filter(assigned_to=request.user)
    for task in tasks:
        if task.due_date:
            events.append({
                'title': f"Task: {task.title}",
                'start': task.due_date.isoformat(),
                'color': '#EF4444' if task.priority == 'Critical' else '#3B82F6',
                'url': f"/admin/portal/" # linking to dashboard for now
            })
            
    # Appointments
    appointments = Appointment.objects.filter(staff=request.user)
    for appt in appointments:
        events.append({
            'title': f"Mtg: {appt.title}",
            'start': appt.start_time.isoformat(),
            'end': appt.end_time.isoformat(),
            'color': '#10B981',
            'url': '/appointment/list/'
        })

    return JsonResponse(events, safe=False)


def workplace_living(request):
    return render(request, 'workplace_living.html')


# --- Phase 17: Team Views ---
from .models import Team, SharedNote
from django.contrib import messages

@login_required
@user_passes_test(is_manager)
def team_list(request):
    teams = Team.objects.all().order_by('-created_at')
    return render(request, 'blood_request/team_list.html', {'teams': teams})

@login_required
@user_passes_test(is_manager)
def team_create(request):
    workspace_id = request.GET.get('workspace') or request.POST.get('workspace')
    workspace = None
    if workspace_id:
        workspace = get_object_or_404(Workspace, id=workspace_id)
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        member_ids = request.POST.getlist('members')
        
        if name:
            team = Team.objects.create(name=name, description=description, created_by=request.user, workspace=workspace)
            if member_ids:
                team.members.set(member_ids)
            from django.contrib import messages
            messages.success(request, f"Team '{name}' created successfully!")
            if workspace:
                return redirect('workspace_detail', slug=workspace.slug)
            return redirect('team_list')
    
    from django.contrib.auth.models import User
    # Filter users based on workspace if applicable
    if workspace:
        users = workspace.members.all()
    else:
        users = User.objects.filter(is_active=True).exclude(is_superuser=True)
        
    return render(request, 'blood_request/team_form.html', {'users': users, 'workspace': workspace})

@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    # Check access: Manager or Member
    if not (is_manager(request.user) or request.user in team.members.all()):
         from django.contrib import messages
         messages.error(request, "Access Denied")
         return redirect('staff_dashboard')
         
    # Kanban Data for Team
    team_members = team.members.all()
    all_team_tasks = Task.objects.filter(assigned_to__in=team_members).order_by('-updated_at')
    
    todo_tasks = all_team_tasks.filter(status='To Do')
    inprogress_tasks = all_team_tasks.filter(status='In Progress')
    done_tasks = all_team_tasks.filter(status='Done')

    return render(request, 'blood_request/team_detail.html', {
        'team': team,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks
    })

@login_required
def shared_note_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        team_ids = request.POST.getlist('teams')
        
        note = SharedNote.objects.create(
            title=title,
            content=content,
            owner=request.user
        )
        if team_ids:
            note.shared_with_teams.set(team_ids)
            
        from django.contrib import messages
        messages.success(request, "Note shared successfully!")
        # Redirect to the first selected team detail or dashboard
        if team_ids:
            return redirect('team_detail', pk=team_ids[0])
        return redirect('staff_dashboard')
    
    user_teams = Team.objects.filter(members=request.user) if not is_manager(request.user) else Team.objects.all()
    # Pre-select team from query param
    initial_team = request.GET.get('team')
    return render(request, 'blood_request/shared_note_form.html', {
        'teams': user_teams, 
        'initial_team': int(initial_team) if initial_team else None
    })

@login_required
def shared_note_detail(request, pk):
    note = get_object_or_404(SharedNote, pk=pk)
    # Check permission (Owner, Shared User, or Shared Team Member)
    has_access = (
        request.user == note.owner or 
        request.user in note.shared_with_users.all() or
        note.shared_with_teams.filter(members=request.user).exists() or
        is_manager(request.user)
    )
    
    if not has_access:
        from django.contrib import messages
        messages.error(request, "You do not have permission to view this note.")
        return redirect('staff_dashboard')
        
    return render(request, 'blood_request/shared_note_detail.html', {'note': note})

@login_required
@user_passes_test(is_manager)
def team_add_member(request, pk):
    team = get_object_or_404(Team, pk=pk)
    from django.contrib.auth.models import User
    
    if request.method == 'POST':
        member_ids = request.POST.getlist('members')
        if member_ids:
            users_to_add = User.objects.filter(id__in=member_ids)
            team.members.add(*users_to_add)
            from django.contrib import messages
            messages.success(request, f"{users_to_add.count()} members added to {team.name}")
        return redirect('team_detail', pk=pk)
    
    # Show users NOT in the team
    available_users = User.objects.filter(is_active=True).exclude(id__in=team.members.values_list('id', flat=True)).exclude(is_superuser=True)
    return render(request, 'blood_request/team_add_member.html', {
        'team': team,
        'available_users': available_users
    })

@login_required
@user_passes_test(is_manager)
def team_remove_member(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    from django.contrib.auth.models import User
    user_to_remove = get_object_or_404(User, pk=user_pk)
    
    if user_to_remove in team.members.all():
        team.members.remove(user_to_remove)
        from django.contrib import messages
        messages.success(request, f"{user_to_remove.username} removed from {team.name}")
    
    return redirect('team_detail', pk=team_pk)


@login_required
def shared_note_detail(request, pk):
    note = get_object_or_404(SharedNote, pk=pk)
    # Access check: Owner OR in shared_with_teams members OR shared_with_users
    has_access = (note.owner == request.user) or \
                 (note.shared_with_users.filter(id=request.user.id).exists()) or \
                 (note.shared_with_teams.filter(members=request.user).exists())
                 
    if not has_access and not is_manager(request.user):
        from django.contrib import messages
        messages.error(request, "Access Denied")
        return redirect('staff_dashboard')
        
    return render(request, 'blood_request/shared_note_detail.html', {'note': note})

# --- Phase 18: Portal User Management ---
@login_required
@user_passes_test(is_manager)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'blood_request/user_list.html', {'users': users})

@login_required
@user_passes_test(is_manager)
def user_add(request):
    if request.method == 'POST':
        from .forms import UserUpdateForm # Using similar form or create new
        # For simplicity, using standard User creation logic here or a specific form
        # But UserUpdateForm is for existing. Let's use UserCreationForm logic adapted.
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role') # Manager or Staff
        
        if username and password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                if role == 'Manager':
                    from django.contrib.auth.models import Group
                    g = Group.objects.get(name='Managers')
                    user.groups.add(g)
                    user.is_staff = True # Managers are staff
                    user.save()
                
                # Create Profile
                StaffProfile.objects.create(user=user)
                
                messages.success(request, f"User {username} created!")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, str(e))
                
    return render(request, 'blood_request/user_form.html')

@login_required
@user_passes_test(is_manager)
def user_edit_portal(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        user_obj.save()
        
        # Phone
        phone = request.POST.get('phone')
        profile, created = StaffProfile.objects.get_or_create(user=user_obj)
        profile.phone_number = phone
        profile.save()
        
        messages.success(request, f"User {user_obj.username} updated!")
        return redirect('user_list')
        
    return render(request, 'blood_request/user_edit.html', {'target_user': user_obj})

def volunteering(request):
    return render(request, "volunteering.html")

