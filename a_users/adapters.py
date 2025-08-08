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
    
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to intercept unknown account emails and create users
        """
        # Check if this is an email being sent and if user doesn't exist
        if email and email.endswith('@student.uts.edu.au'):
            try:
                User.objects.get(email=email)
                # User exists, send normal email
            except User.DoesNotExist:
                # User doesn't exist, create them
                username = email.split('@')[0].split('.')[0]
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    is_active=True
                )
                
                # Set random password
                random_password = ''.join(secrets.choice(
                    string.ascii_letters + string.digits + string.punctuation
                ) for _ in range(50))
                user.set_password(random_password)
                user.save()
                
                # Create EmailAddress record as VERIFIED so they can get codes
                EmailAddress.objects.create(
                    user=user,
                    email=email,
                    verified=True,
                    primary=True
                )
                
                # Don't send unknown account email, instead send login code
                if 'unknown' in template_prefix.lower() or 'no account' in template_prefix.lower():
                    # Send login code using allauth's internal method
                    request = context.get('request')
                    if request:
                        try:
                            # Use allauth's internal login code sending
                            from allauth.account.internal.flows.login_by_code import send_login_code
                            send_login_code(request, user, email)
                        except ImportError:
                            # Fallback - use the render_mail method to send login code template
                            login_code = self.generate_login_code()
                            # Store the code (you might need to implement this storage)
                            # For now, let's just send the code template
                            super().send_mail('account/email/login_code', email, {
                                **context,
                                'user': user,
                                'code': login_code
                            })
                    return  # Don't send the original unknown account email
        
        # Send normal email for all other cases
        super().send_mail(template_prefix, email, context)
    
    def is_email_verified(self, request, email):
        """
        For login-by-code, if they can receive and enter the code, they're verified
        """
        return True