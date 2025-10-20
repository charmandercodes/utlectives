"""
URL configuration for a_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# urls.py
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import RedirectView
from a_users.views import restart_login, signup_with_fresh_session, redirect_to_login_code, CustomSignupView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name='course-list', permanent=False)),  # Redirect to named URL
    path("admin/", admin.site.urls),
    path('users/', include('a_users.urls')),
    path('reviews/', include('a_reviews.urls')),
    path('accounts/login/', redirect_to_login_code, name='account_login'),
    path('signup-fresh/', signup_with_fresh_session, name='signup_fresh'),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('restart-login/', restart_login, name='restart_login'),
    path('accounts/', include('allauth.urls')),
    path('silk/', include('silk.urls', namespace='silk'))
]
# Note: This assumes you have a URL named 'home' in your a_reviews.urls with namespace 'reviews'
# If your reviews URLs don't use a namespace, just use pattern_name='home' or whatever the URL name is
