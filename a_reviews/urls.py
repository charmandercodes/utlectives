
from django.urls import path
from .views import *

urlpatterns = [
    path('', course_list, name='course-list'),
    path('courses/<str:code>/', course_details, name="course-detail"),
    path('courses/create-review/<str:code>/', review_create_view,  name="create-review"),
    path('courses/htmx-create-review/<str:code>/', htmx_create_review, name="htmx-create-review"),
    path('search', search_courses, name='search'),
    path('htmx/delete-review-modal/<int:review_id>/', htmx_delete_review_modal, name='htmx-delete-review-modal'),
    path('htmx/delete-review/<int:review_id>/', htmx_delete_review, name='htmx-delete-review'),
    path('htmx/update-review-modal/<int:review_id>/', htmx_update_review_modal, name='htmx-update-review-modal'),
    path('htmx/update-review/<int:review_id>/', htmx_update_review, name='htmx-update-review'),
]
