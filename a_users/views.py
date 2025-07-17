from django.shortcuts import redirect, render
from django.http import HttpResponse
from a_reviews.models import Review
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from a_reviews.forms import ReviewForm
from django.contrib.auth import logout
from allauth.account.utils import send_email_confirmation
from django.views.decorators.http import require_POST
from allauth.account.forms import ChangePasswordForm
from django_htmx.http import HttpResponseClientRedirect

from a_users.forms import UpdateUsernameForm
# Create your views here.



# Basic page views

@login_required 
def user_page(request):
    # Handle both GET and POST requests
    if request.method == 'POST':
        # If it's a POST request, redirect to GET (POST-Redirect-GET pattern)
        return redirect('user-page')  # Replace with your actual URL name
    
    # GET request (normal page load)
    user_reviews = Review.objects.filter(author=request.user).select_related('course').order_by('-review_date')
    
    context = {
        'reviews': user_reviews,
        'reviews_count': user_reviews.count(),
    }
    return render(request, 'a_users/user.html', context)

def terms_and_conditions_page(request):
    return render(request, 'pages/terms.html')


# Review Views 

def delete_review(request, review_id):
    review = Review.objects.get(id=review_id)

    if request.method == 'POST':
        review.delete()
        return redirect('user-page')
    
    return render(request, 'a_users/review_confirm_delete.html', {'review': review})

def update_users_review(request, review_id):
    # get the review with the id we specified in the url for updating
    review = Review.objects.get(id=review_id)
    course = review.course  # Get the course from the review
    
    # instantiate the form with the review object data
    form = ReviewForm(instance=review)

    # if the request is post, then feed the form with the request data using the instance of the review object
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            # save the form
            form.save()
            return redirect('user-page')

    # pass both form and course to the template
    return render(request, 'a_reviews/review_form.html', {
        'form': form, 
        'course': course,
        'is_update': True  # Optional flag to differentiate between create/update
    })


# Account views 


# Update Username


@login_required
def change_password_inline(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            response = render(request, 'a_users/partials/change-password.html', {
                'form': None,
                'hide': False,
                'show_edited': False
            })
            response['HX-Trigger'] = 'passwordChanged'
            return response
        else:
            return render(request, 'a_users/partials/change-password.html', {
                'form': form,
                'show_edited': True,
                'hide': True
            })
    
    form = ChangePasswordForm(user=request.user)
    return render(request, 'a_users/partials/change-password.html', {
        'form': form,
        'hide': False,
        'show_edited': False
    })

# @login_required
# def update_username(request):
#     if request.method == 'POST':
#         new_username = request.POST.get('username', '').strip()
        
#         if not new_username:
#             messages.error(request, 'Username cannot be empty.')
#             return redirect('user-page')
        
#         # Basic security validation
#         import re
        
#         # Length check
#         if len(new_username) < 3 or len(new_username) > 30:
#             messages.error(request, 'Username must be 3-30 characters.')
#             return redirect('user-page')
        
#         # Only allow safe characters
#         if not re.match(r'^[a-zA-Z0-9_-]+$', new_username):
#             messages.error(request, 'Username can only contain letters, numbers, underscores, and hyphens.')
#             return redirect('user-page')
        
#         # Check if username already exists
#         if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
#             messages.error(request, 'Username already taken.')
#         else:
#             request.user.username = new_username
#             request.user.save()
#             messages.success(request, 'Username updated successfully!')
    
#     return render(request, 'a_users/components/update-username.html')

@login_required
def update_username_inline(request):
    if request.method == 'POST':
        form = UpdateUsernameForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            response = render(request, 'a_users/oob/update-username-with-title.html')
            response['HX-Trigger'] = 'usernameUpdated'
            return response
        else:
            return render(request, 'a_users/components/update-username.html', {'form': form})
    
    form = UpdateUsernameForm(user=request.user)
    return render(request, 'a_users/components/update-username.html', {'form': form})

# Delete Account 

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user

        # Log the user out first
        logout(request)
        
        # Delete the user account
        user.delete()
        
        # Add a message (will be shown on redirect page)
        messages.success(request, 'Your account has been successfully deleted.')
        
        # Redirect to homepage or login page
        return redirect('course-list')
    
    # If GET request, redirect back to account page
    return redirect('user-page')


@login_required
def change_password_inline(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            response = render(request, 'a_users/partials/change-password.html', {
                'form': None,
                'hide': False,
                'show_edited': False
            })
            response['HX-Trigger'] = 'passwordChanged'
            return response
        else:
            return render(request, 'a_users/partials/change-password.html', {
                'form': form,
                'show_edited': True,
                'hide': True
            })
    
    form = ChangePasswordForm(user=request.user)
    return render(request, 'a_users/partials/change-password.html', {
        'form': form,
        'hide': False,
        'show_edited': False
    })


