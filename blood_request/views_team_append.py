
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
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        member_ids = request.POST.getlist('members')
        
        if name:
            team = Team.objects.create(name=name, description=description, created_by=request.user)
            if member_ids:
                team.members.set(member_ids)
            messages.success(request, f"Team '{name}' created successfully!")
            return redirect('team_list')
    
    users = User.objects.filter(is_active=True).exclude(is_superuser=True)
    return render(request, 'blood_request/team_form.html', {'users': users})

@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    # Check access: Manager or Member
    if not (is_manager(request.user) or request.user in team.members.all()):
         messages.error(request, "Access Denied")
         return redirect('staff_dashboard')
         
    return render(request, 'blood_request/team_detail.html', {'team': team})
