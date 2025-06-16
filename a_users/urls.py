from django.urls import path
from . import views


urlpatterns = [
    path('', views.userView , name='user-page'),
    path('termsandconditions/', views.termsView, name='terms-and-conditions')
]
