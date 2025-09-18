# In your views.py or signals.py
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from django.contrib import messages

from a_reviews.models import Review


@receiver(user_logged_in)
def custom_login_message(request, user, **kwargs):
    messages.success(request, f"Signed in as: {user.username}!")

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Review)
def update_course_ratings_on_review_delete(sender, instance, **kwargs):
    instance.course.update_ratings()