from django.shortcuts import render

from a_reviews.models import Course

# Create your views here.


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'a_reviews/page.html', {'courses': courses})
