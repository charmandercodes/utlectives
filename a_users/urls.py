from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_page, name='user-page'),
    path('termsandconditions/', views.terms_and_conditions_page, name='terms-and-conditions'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete-review'),
    path('update-review/<int:review_id>/', views.update_users_review, name='update-review'),
    path('update-username/', views.update_username_inline, name='update-username'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('change-password/', views.change_password_inline, name='change_password_inline'),
]
