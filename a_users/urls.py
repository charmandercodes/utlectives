from django.urls import path
from . import views


urlpatterns = [
    path('', views.basicView , name='basic-view'),
    path('termsandconditions/', views.termsView, name='terms-and-conditions')
]
