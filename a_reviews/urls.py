
from django.urls import path
from .views import *

urlpatterns = [
    path('', course_list, name='course-list'),
    path('courses/filter/', filter_courses, name='filter_courses'),  # Move this up!
    path('courses/<str:code>/', course_details, name="course-detail"),  # Keep this after specific routes
    path('courses/create-review/<str:code>/', review_create_view,  name="create-review"),
    path('courses/htmx-create-review/<str:code>/', htmx_create_review, name="htmx-create-review"),
    # deprecated search function
    # path('search', search_courses, name='search'),
    path('htmx/delete-review-modal/<int:review_id>/', htmx_delete_review_modal, name='htmx-delete-review-modal'),
    path('htmx/delete-review/<int:review_id>/', htmx_delete_review, name='htmx-delete-review'),
    path('htmx/update-review-modal/<int:review_id>/', htmx_update_review_modal, name='htmx-update-review-modal'),
    path('htmx/update-review/<int:review_id>/', htmx_update_review, name='htmx-update-review'),
    path('course/<str:course_code>/header/', refresh_course_header, name='refresh-course-header'),
]