from django.urls import path
from . import views


urlpatterns = [
    path('', views.userView , name='user-page'),
    path('termsandconditions/', views.termsView, name='terms-and-conditions'),
    path('delete-review/<int:review_id>/', views.deleteUserView, name='delete-review'),
    path('update-review/<int:review_id>/', views.update_users_review, name='update-review'),
]
