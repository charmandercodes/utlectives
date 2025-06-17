from django.shortcuts import get_object_or_404, redirect, render

from a_reviews.forms import ReviewForm
from a_reviews.models import Course, Review

# Create your views here.

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'a_reviews/home.html', {'courses': courses})

def course_details(request, code):
    course = get_object_or_404(Course, code=code)
    reviews = course.review_set.all().order_by('-review_date')  # Get all reviews for this course
    
    context = {
        'course': course,
        'reviews': reviews,
    }
    
    return render(request, 'a_reviews/detail.html', context)



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

