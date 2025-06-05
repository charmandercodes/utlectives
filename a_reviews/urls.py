
from django.urls import path
from .views import course_list, course_details

urlpatterns = [
    path('', course_list, name='course-list'),
    path('courses/<str:code>/', course_details, name="course-detail")
]
