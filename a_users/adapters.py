from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import secrets
import string

from django.shortcuts import resolve_url
from django.conf import settings

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


from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.
        """
        # Use allauth's built-in method to get the next URL safely
        redirect_url = super().get_login_redirect_url(request)
        if redirect_url and redirect_url != '/':
            return redirect_url
        
        # Check for next parameter in GET or POST as fallback
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url and self.is_safe_url(next_url):
            return next_url
        
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    
    def get_signup_redirect_url(self, request):
        """
        Returns the default URL to redirect to after signing up.
        This is the key method that handles signup redirects.
        """
        # Check for next parameter in GET or POST
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url and self.is_safe_url(next_url):
            return next_url
        
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    
    def is_safe_url(self, url):
        """
        Override to allow your local development URLs
        """
        try:
            from django.utils.http import url_has_allowed_host_and_scheme
        except ImportError:
            from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme

        # Allow relative URLs and your local development server
        return url_has_allowed_host_and_scheme(
            url, 
            allowed_hosts={'127.0.0.1:8000', 'localhost:8000', None}  # None allows relative URLs
        )
