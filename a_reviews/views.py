from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from a_reviews.filters import CourseFilter, ReviewFilter
from a_reviews.forms import ReviewForm
from a_reviews.models import Course, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings



# Create your views here.

# CUD Views for Reviews 

# Create 
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
        
        # Update course ratings after new review
        course.update_ratings()
        
        # Prepare context for both the new review AND the updated header
        user_review = review  # User now has a review
        context = {
            'reviews': [review],
            'course': course,  # Updated course with new ratings
            'user_review': user_review,  # For header logic
        }
        
        # This template will render both the review AND the header
        response = render(request, 'a_reviews/detail_components/review_with_header.html', context)
        
        # Close modal
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

# Delete 
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


# Update 
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
    

# Read - Course Views 

# view that returns initial course list 
from django.db.models import Case, When, Value, BooleanField

def course_list(request):
    courses = Course.objects.annotate(
        session_available=Case(
            When(~Q(sessions=[]), then=Value(True)),  # not empty list
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('-session_available', '-overall_rating', '-review_count')

    paginator = Paginator(courses, settings.PAGE_SIZE)
    course_page = paginator.page(1)
    
    return render(request, 'a_reviews/home.html', {'courses': course_page})


# view that returns a filtered list of courses 
def filter_courses(request):
    """
    Handle course filtering, searching, and sorting using django-filters
    """
    # Create the filter instance
    course_filter = CourseFilter(request.GET, queryset=Course.objects.all())
    
    # Get the filtered and sorted queryset
    filtered_courses = course_filter.qs
    
    # Handle pagination
    page_list = request.GET.getlist('page')
    if page_list:
        try:
            page_number = max(int(p) for p in page_list if p.isdigit())
        except:
            page_number = 1
    else:
        page_number = 1
    
    # Apply pagination
    paginator = Paginator(filtered_courses, settings.PAGE_SIZE)
    try:
        course_page = paginator.page(page_number)
    except:
        course_page = paginator.page(1)
    
    # Debug logging (optional)
    print(f"Applied filters: {dict(request.GET)}")
    print(f"Filtered course count: {filtered_courses.count()}")
    print(f"Showing page {page_number} of {paginator.num_pages}")
    
    return render(request, 'a_reviews/course_list.html', {
        'courses': course_page,
        'filter': course_filter
    })



# view for infinite scroll with persistent filtering of new items
def get_courses(request):
    """
    Handle infinite scroll pagination with filtering
    """
    page = request.GET.get('page', 1)
    
    # Use the same filtering logic as filter_courses
    course_filter = CourseFilter(request.GET, queryset=Course.objects.all())
    filtered_courses = course_filter.qs
    
    # Apply pagination
    paginator = Paginator(filtered_courses, settings.PAGE_SIZE)
    
    try:
        course_page = paginator.page(page)
    except:
        course_page = paginator.page(1)
    
    context = {
        'courses': course_page
    }
    
    return render(request, 'a_reviews/course_list.html', context)


# Read - Review 

# views that returns initial course reviews page 
def course_details(request, code):
    course = get_object_or_404(Course, code=code)
    reviews = course.review_set.all().order_by('-review_date')
    form = ReviewForm()


    paginator = Paginator(reviews, settings.PAGE_SIZE)
    reviews = paginator.page(1)

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


# View that returns a filtered list of reviews
def filter_reviews(request, code):
    course = get_object_or_404(Course, code=code)
    reviews_queryset = course.review_set.all()
    
    review_filter = ReviewFilter(request.GET, queryset=reviews_queryset)
    filtered_reviews = review_filter.qs
    
    if not request.GET.get('sort'):
        filtered_reviews = filtered_reviews.order_by('-review_date')
    
    paginator = Paginator(filtered_reviews, settings.PAGE_SIZE)
    review_page = paginator.page(1)
    
    context = {
        'reviews': review_page,
        'course': course,
    }
    
    return render(request, 'a_reviews/detail_components/review.html', context)



# view for infinite scroll with persistent filtering of new items
def get_reviews(request):
    """
    Handle infinite scroll pagination for reviews with filtering
    """
    page = request.GET.get('page', 1)
    course_code = request.GET.get('course_code')
    
    course = get_object_or_404(Course, code=course_code)
    reviews_queryset = course.review_set.all()
    
    # Apply the same filtering logic as filter_reviews
    review_filter = ReviewFilter(request.GET, queryset=reviews_queryset)
    filtered_reviews = review_filter.qs
    
    # If no sort specified, default to most recent
    if not request.GET.get('sort'):
        filtered_reviews = filtered_reviews.order_by('-review_date')
    
    paginator = Paginator(filtered_reviews, settings.PAGE_SIZE)
    
    try:
        review_page = paginator.page(page)
    except:
        review_page = paginator.page(1)
    
    context = {
        'reviews': review_page,
        'course': course,
    }
    
    return render(request, 'a_reviews/detail_components/review.html', context)


# htmx out of band swap that updates the button from 'write a review' to 'view your reviews'
# as soon as review is submitted from modal (uses htmx to avoid page reload of that state)

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




# Deprecated - To Delete Views 

# @login_required
# def review_create_view(request, code):  # Accept course code parameter
#     course = get_object_or_404(Course, code=code)  # Get the specific course
    
#     # Check if user already reviewed this course (optional)
#     # if Review.objects.filter(course=course, author=request.user).exists():
#     #     # User already reviewed this course
#     #     return redirect('course-detail', code=code)
    
#     if request.method == "POST":
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)  # Don't save to DB yet
#             review.course = course           # Set the course
#             review.author = request.user     # Set the author
#             review.save()                    # Now save to DB
#             return redirect('course-detail', code=code)  # Redirect to course page
#     else:
#         form = ReviewForm()
    
#     context = {
#         'form': form,
#         'course': course,
#         'is_update': False  # Add this flag for create view
#     }
#     return render(request, 'a_reviews/review_form.html', context)


# deprecated search
# def search_courses(request):
#     query = request.GET.get('search', '')

#     courses = Course.objects.filter(
#         Q(name__icontains=query)
#     )

#     return render(request, 'a_reviews/course_list.html', {'courses': courses})
