from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()

class UTSPasswordlessAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        # Only allow UTS student emails
        if not email.endswith('@student.uts.edu.au'):
            raise ValidationError("Only UTS student emails (@student.uts.edu.au) are allowed.")
        return email
    
    def save_user(self, request, user, form, commit=True):
        # Create user with random password (they'll never need to know it)
        user = super().save_user(request, user, form, commit=False)
        
        # Generate a secure random password
        random_password = ''.join(secrets.choice(
            string.ascii_letters + string.digits + string.punctuation
        ) for _ in range(50))
        user.set_password(random_password)
        
        if commit:
            user.save()
        return user