
from django.urls import path
from .views import *

urlpatterns = [
    
    # Create Update Delete - Reviews
    # Create 
    path('courses/htmx-create-review/<str:code>/', htmx_create_review, name="htmx-create-review"),
    # Delete
    path('htmx/delete-review-modal/<int:review_id>/', htmx_delete_review_modal, name='htmx-delete-review-modal'),
    path('htmx/delete-review/<int:review_id>/', htmx_delete_review, name='htmx-delete-review'),
    # Update
    path('htmx/update-review-modal/<int:review_id>/', htmx_update_review_modal, name='htmx-update-review-modal'),
    path('htmx/update-review/<int:review_id>/', htmx_update_review, name='htmx-update-review'),
    
    # Read - Courses
    path('', course_list, name='course-list'),
    path('courses/filter/', filter_courses, name='filter_courses'),  
    path('get-courses/', get_courses, name='get-courses'),
    
    # Read - Reviews
    path('courses/<str:code>/', course_details, name="course-detail"), 
    path('course/<str:code>/reviews/filter/', filter_reviews, name='filter_reviews'),
    path('get-reviews/', get_reviews , name='get-reviews'),
    
    # OOB Swap
    path('course/<str:course_code>/header/', refresh_course_header, name='refresh-course-header'),
]