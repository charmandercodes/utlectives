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
    reviews = course.review_set.all().order_by('-review_date')  # Get all reviews for this course
    form = ReviewForm()  # Initialize the form for creating a new review
    
    context = {
        'course': course,
        'reviews': reviews,
        'form': form,
    }
    
    return render(request, 'a_reviews/detail.html', context)


@login_required
def search_courses(request):
    query = request.GET.get('search', '')

    courses = Course.objects.filter(
        Q(name__icontains=query)
    )

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
        
        # Fix: Pass as a list
        context = {'reviews': [review]}  # Put the review in a list
        return render(request, 'a_reviews/detail_components/review.html', context)
    else:
        print(f"Form errors: {form.errors}")
        context = {
            'form': form,
            'course': course,
            'is_update': False
        }
        return render(request, 'a_reviews/partials/review-modal.html', context)