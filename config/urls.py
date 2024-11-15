"""
URL configuration for testPAS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
import os, sys
from django.contrib import admin
# from . import views
# from django.contrib import views as auth_views
from django.urls import path, include
# from testpas import views as auth_views
from testpas import views
#import testpas.views as views
# from django.contrib.auth import views as views
app_name = 'testpas'

urlpatterns = [
    path('', views.index, name="index"),
    path('api/send_token_email/', views.send_token_email, name='send_token_email'),
    path('survey/<int:survey_id>/start/', views.start_survey, name='start_survey'),
    path('survey/<int:survey_id>/questions/', views.survey_questions, name='survey_questions'),
    path('survey/<int:survey_id>/complete/', views.survey_complete, name='survey_complete'),
    path('create-account/', views.create_account, name='create_account'),  # New URL path for account creation
    # path('login/', views.login_view, name='login'),  # New URL path for login
    path('admin/', admin.site.urls),
    # path('404', views.FourZeroFour, name="404")
]
    # path('', include('https://git.heroku.com/testpas.git')),
