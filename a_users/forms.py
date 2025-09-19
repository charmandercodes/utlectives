from django import forms
from allauth.account.forms import SignupForm
import re
from django.core.exceptions import ValidationError

from a_users.adapters import User

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password fields for passwordless authentication
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            return email
        
        # Validate UTS email domain
        if not email.endswith('@student.uts.edu.au'):
            raise forms.ValidationError(
                'Only UTS student emails (@student.uts.edu.au) are allowed to register.'
            )
        
        # Optional: Additional regex validation for extra security
        pattern = r'^[a-zA-Z0-9._%+-]+@student\.uts\.edu\.au$'
        if not re.match(pattern, email):
            raise forms.ValidationError(
                'Please enter a valid UTS student email address.'
            )
        
        # Check if email already exists in User model
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists. "
                "Please sign in instead or use a different email address."
            )
        
        # Also check EmailAddress model for verified/unverified emails
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists. "
                "Please sign in instead or use a different email address."
            )
        
        return email
    
    def save(self, request):
        # Call the parent save method
        user = super().save(request)
        # Set an unusable password since we're not using passwords
        user.set_unusable_password()
        user.save()
        # You can add additional processing here if needed
        return user

class UpdateUsernameForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Enter new username'
        })
    )
    
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
    
    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        
        if not username:
            raise ValidationError('Username cannot be empty.')
        
        # Only allow safe characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError('Username can only contain letters, numbers, underscores, and hyphens.')
        
        # Check if username already exists (excluding current user)
        if User.objects.filter(username=username).exclude(id=self.user.id if self.user else None).exists():
            raise ValidationError('Username already taken.')
        
        return username
    
    def save(self):
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.save()
            return self.user



