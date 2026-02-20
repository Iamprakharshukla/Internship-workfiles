from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Workspace, WorkspaceMember, Team, Project
from django.utils.text import slugify
from .views import is_manager
from django.contrib.auth.decorators import user_passes_test

@login_required
def workspace_list(request):
    """List all workspaces the user is a member of."""
    memberships = WorkspaceMember.objects.filter(user=request.user)
    workspaces = [m.workspace for m in memberships]
    return render(request, 'workspace/workspace_list.html', {'workspaces': workspaces})

@login_required
@user_passes_test(is_manager)
def workspace_create(request):
    """Create a new workspace."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            slug = slugify(name)
            if Workspace.objects.filter(slug=slug).exists():
                messages.error(request, "A workspace with this name already exists.")
                return redirect('workspace_create')
                
            workspace = Workspace.objects.create(
                name=name, 
                slug=slug, 
                description=description, 
                owner=request.user
            )
            # Add owner as Admin
            WorkspaceMember.objects.create(workspace=workspace, user=request.user, role='Admin')
            
            messages.success(request, f"Workspace '{name}' created!")
            return redirect('workspace_detail', slug=workspace.slug)
            
    return render(request, 'workspace/workspace_create.html')

@login_required
def workspace_detail(request, slug):
    """Main Jira-like Dashboard for a Workspace."""
    workspace = get_object_or_404(Workspace, slug=slug)
    
    # Check access
    if not WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists():
        messages.error(request, "Access Denied")
        return redirect('workspace_list')
        
    members = WorkspaceMember.objects.filter(workspace=workspace)
    teams = workspace.teams.all()
    # Assuming Projects will be linked to Workspace soon, for now list all or filter
    # For MVP, listing all projects where user is manager as a placeholder
    projects = request.user.managed_projects.all()
    
    return render(request, 'workspace/workspace_detail.html', {
        'workspace': workspace,
        'members': members,
        'teams': teams,
        'projects': projects
    })

@login_required
def workspace_invite(request, slug):
    """Invite users to workspace."""
    workspace = get_object_or_404(Workspace, slug=slug)
    
    # Check Admin Access
    membership = WorkspaceMember.objects.filter(workspace=workspace, user=request.user).first()
    if not membership or membership.role != 'Admin':
        messages.error(request, "Only Admins can invite members.")
        return redirect('workspace_detail', slug=slug)
        
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'Member')
        
        try:
            user = User.objects.get(username=username)
            if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
                messages.warning(request, "User is already a member.")
            else:
                WorkspaceMember.objects.create(workspace=workspace, user=user, role=role)
                messages.success(request, f"User {username} added as {role}.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            
    return redirect('workspace_detail', slug=slug)
