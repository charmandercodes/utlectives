
from django.urls import path
from .views import course_list, course_details, review_create_view

urlpatterns = [
    path('', course_list, name='course-list'),
    path('courses/<str:code>/', course_details, name="course-detail"),
    path('courses/create-review/<str:code>/', review_create_view,  name="create-review")

]
