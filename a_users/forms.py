from django import forms
from allauth.account.forms import SignupForm
import re


class CustomSignupForm(SignupForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email:
            # Check if email ends with @student.uts.edu.au
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
        
        return email
    
    def save(self, request):
        # Call the parent save method
        user = super().save(request)
        # You can add additional processing here if needed
        return user


