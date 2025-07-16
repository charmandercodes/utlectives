# In your views.py or signals.py
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from django.contrib import messages


@receiver(user_logged_in)
def custom_login_message(request, user, **kwargs):
    messages.success(request, f"Signed in as: {user.username}!")