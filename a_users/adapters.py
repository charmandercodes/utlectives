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
    
    def clean_email(self, email):
        # Only allow UTS student emails
        if not email.endswith('@student.uts.edu.au'):
            raise ValidationError("Only UTS student emails (@student.uts.edu.au) are allowed.")
        
        # Create user immediately if they don't exist
        if email.endswith('@student.uts.edu.au'):
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0].split('.')[0],
                    'is_active': True,
                }
            )
            
            if created:
                # Set random password
                random_password = ''.join(secrets.choice(
                    string.ascii_letters + string.digits + string.punctuation
                ) for _ in range(50))
                user.set_password(random_password)
                user.save()
                
                # Create EmailAddress record as VERIFIED
                EmailAddress.objects.create(
                    user=user,
                    email=email,
                    verified=True,
                    primary=True
                )
        
        return email
    
    def send_mail(self, template_prefix, email, context):
        """Store email in session and provide full URLs"""
        request = context.get('request')
        if request and email:
            request.session['verification_email'] = email
            
            # Add full signup URL to context for unknown account emails
            if 'unknown' in template_prefix.lower():
                from django.urls import reverse
                signup_path = reverse('signup_fresh')
                signup_url = request.build_absolute_uri(signup_path)
                context['signup_url'] = signup_url
        
        super().send_mail(template_prefix, email, context)
    
    # Keep your other methods (get_login_redirect_url, etc.)
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