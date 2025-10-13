from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import secrets
import string
from django.shortcuts import resolve_url
from django.conf import settings
from allauth.account.models import EmailAddress

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):

    
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new User instance using information provided in the
        signup form and extracts username from email.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Extract and format username from email
        if user.email:
            # Get the part before @ and before the first .
            username_part = user.email.split('@')[0].split('.')[0]
            user.username = username_part.capitalize()
        
        if commit:
            user.save()
        
        return user
    
    def get_login_redirect_url(self, request):
        redirect_url = super().get_login_redirect_url(request)
        if redirect_url and redirect_url != '/':
            return redirect_url
        
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url and self.is_safe_url(next_url):
            return next_url
        
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    
    def get_signup_redirect_url(self, request):
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url and self.is_safe_url(next_url):
            return next_url
        
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    
    def is_safe_url(self, url):
        try:
            from django.utils.http import url_has_allowed_host_and_scheme
        except ImportError:
            from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme

        return url_has_allowed_host_and_scheme(
            url, 
            allowed_hosts={'127.0.0.1:8000', 'localhost:8000', None}
        )