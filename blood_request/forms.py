from django import forms
from django.contrib.auth.models import User
from .models import StaffProfile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-red'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-red'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-red'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-brand-red focus:border-brand-red'}),
        }
