from django import forms
from django.contrib.auth.models import User


from .models import StaffProfile, SharedNote, Team, Task
from django_ckeditor_5.widgets import CKEditor5Widget

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
        }

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(is_superuser=True),
        required=False,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'})
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
        required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
        }

from .models import Blog
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue', 'rows': 3}),
            'content': CKEditor5Widget(config_name='extends'),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue'}),
        }

class SharedNoteForm(forms.ModelForm):
    # Custom queryset filtering for teams/users can be done in __init__ if needed
    shared_with_teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    shared_with_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(is_superuser=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = SharedNote
        fields = ['title', 'content', 'shared_with_teams', 'shared_with_users']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-blue mb-4'}),
            'content': CKEditor5Widget(config_name='extends'),
        }
