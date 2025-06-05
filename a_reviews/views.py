from django.shortcuts import get_object_or_404, render

from a_reviews.models import Course

# Create your views here.


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'a_reviews/page.html', {'courses': courses})

def course_details(request, code):
    course = get_object_or_404(Course, code=code)
    return render(request, 'a_reviews/detail.html', {'course': course})
