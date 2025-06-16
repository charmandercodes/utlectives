from allauth.account.forms import SignupForm
from django import forms

class PasswordlessSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password fields
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def save(self, request):
        # Create user without requiring password input
        user = super().save(request)
        return user