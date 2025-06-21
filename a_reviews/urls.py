
from django.urls import path
from .views import *

urlpatterns = [
    path('', course_list, name='course-list'),
    path('courses/<str:code>/', course_details, name="course-detail"),
    path('courses/create-review/<str:code>/', review_create_view,  name="create-review"),
    path('courses/htmx-create-review/<str:code>/', htmx_create_review, name="htmx-create-review"),
    path('search', search_courses, name='search'),
]
