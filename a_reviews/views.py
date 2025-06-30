from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from a_reviews.forms import ReviewForm
from a_reviews.models import Course, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.

import logging
logger = logging.getLogger(__name__)

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'a_reviews/home.html', {'courses': courses})

def course_details(request, code):
    course = get_object_or_404(Course, code=code)
    reviews = course.review_set.all().order_by('-review_date')
    form = ReviewForm()
    
    # Check if the current user has already reviewed this course
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(course=course, author=request.user)
        except Review.DoesNotExist:
            user_review = None
    
    context = {
        'course': course,
        'reviews': reviews,
        'form': form,
        'user_review': user_review,  # Pass this to the template
        'is_update': user_review is not None,  # For the modal header
    }
    
    return render(request, 'a_reviews/detail.html', context)


# deprecated search
# def search_courses(request):
#     query = request.GET.get('search', '')

#     courses = Course.objects.filter(
#         Q(name__icontains=query)
#     )

#     return render(request, 'a_reviews/course_list.html', {'courses': courses})


def filter_courses(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get filter parameters
    selected_faculties = request.GET.getlist('faculty')
    selected_sessions = request.GET.getlist('session')
    
    print(f"Search query: '{search_query}'")
    print(f"Selected sessions: {selected_sessions}")
    print(f"Selected faculties: {selected_faculties}")
    
    # Start with all courses
    courses = Course.objects.all()
    
    # Apply filters FIRST (this creates the "context")
    if selected_faculties:
        courses = courses.filter(faculty__in=selected_faculties)
        print(f"After faculty filter: {courses.count()} courses")
    
    if selected_sessions:
        course_ids = []
        for course in courses:
            if any(session in course.sessions for session in selected_sessions):
                course_ids.append(course.id)
        courses = Course.objects.filter(id__in=course_ids)
        print(f"After session filter: {courses.count()} courses")
    
    # Apply search WITHIN the filtered results
    if search_query:
        courses = courses.filter(Q(name__icontains=search_query))
        print(f"After search within filters: {courses.count()} courses")
    
    print(f"Final course count: {courses.count()}")
    return render(request, 'a_reviews/course_list.html', {'courses': courses})

@login_required
def review_create_view(request, code):  # Accept course code parameter
    course = get_object_or_404(Course, code=code)  # Get the specific course
    
    # Check if user already reviewed this course (optional)
    # if Review.objects.filter(course=course, author=request.user).exists():
    #     # User already reviewed this course
    #     return redirect('course-detail', code=code)
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)  # Don't save to DB yet
            review.course = course           # Set the course
            review.author = request.user     # Set the author
            review.save()                    # Now save to DB
            return redirect('course-detail', code=code)  # Redirect to course page
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'course': course,
        'is_update': False  # Add this flag for create view
    }
    return render(request, 'a_reviews/review_form.html', context)

@login_required
@require_http_methods(["POST"])
def htmx_create_review(request, code):
    course = get_object_or_404(Course, code=code)
    
    form = ReviewForm(request.POST)
    
    if form.is_valid():
        review = form.save(commit=False)
        review.course = course
        review.author = request.user
        review.save()
        
        # Create the response with the new review
        context = {'reviews': [review]}
        response = render(request, 'a_reviews/detail_components/review.html', context)
        
        # Add the HX-Trigger header to close the modal
        response["HX-Trigger"] = "closeModal"
        return response
    else:
        print(f"Form errors: {form.errors}")
        context = {
            'form': form,
            'course': course,
            'is_update': False
        }
        response = render(request, 'a_reviews/partials/review-modal.html', context)
        response['HX-Retarget'] = "#contact_modal"
        response["HX-Reswap"] = "outerHTML"
        response["HX-Trigger-After-Settle"] = 'fail'
        return response




@login_required
@require_http_methods(["GET"])
def htmx_delete_review_modal(request, review_id):
    """Load the delete confirmation modal with review details"""
    review = get_object_or_404(Review, id=review_id, author=request.user)
    
    context = {
        'review': review,
    }
    
    return render(request, 'a_reviews/partials/delete-modal-content.html', context)

@login_required
@require_http_methods(["DELETE"])
def htmx_delete_review(request, review_id):
    """Handle the actual review deletion"""
    review = get_object_or_404(Review, id=review_id, author=request.user)
    
    # Store the review ID for logging or response
    deleted_review_id = review.id
    
    # Delete the review
    review.delete()
    
    # Return an empty response (the review div will be removed)
    response = HttpResponse('')
    response.status_code = 200
    
    return response

@login_required
@require_http_methods(["GET"])
def htmx_update_review_modal(request, review_id):
    review = get_object_or_404(Review, id=review_id, author=request.user)
    form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'course': review.course,  # ✅ Add the course object
        'is_update': True
    }
    
    return render(request, 'a_reviews/partials/edit-modal-content.html', context)

@login_required
@require_http_methods(["PUT", "POST"])
def htmx_update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, author=request.user)
    
    if request.method == "PUT":
        from django.http import QueryDict
        put_data = QueryDict(request.body)
        form = ReviewForm(put_data, instance=review)
    else:
        form = ReviewForm(request.POST, instance=review)
    
    if form.is_valid():
        updated_review = form.save()
        
        # Check if user now has a review (they should after saving)
        user_review = updated_review  # Since they just updated their review
        
        # Pass ALL needed context for both review AND header
        context = {
            'reviews': [updated_review], 
            'show_edit_buttons': True,
            'course': updated_review.course,  # Add course for header
            'user_review': user_review,       # Add user_review for header logic
        }
        response = render(request, 'a_reviews/oob/update_response.html', context)
        
        # Fix the trigger issue - use JSON for multiple triggers
        import json
        response["HX-Trigger"] = json.dumps({
            "closeEditModal": {},
        })
        return response
    else:
        context = {
            'review': review,
            'course': review.course,
            'form': form,
            'is_update': True
        }
        return render(request, 'a_reviews/partials/edit-modal-content.html', context)
    


def refresh_course_header(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(course=course, author=request.user)
        except Review.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'user_review': user_review,
    }
    return render(request, 'a_reviews/detail_components/review_header.html', context)