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
    path('', views.questionnaire_interest, name="index"),
    path('create-account/', views.create_account, name='create_account'),
    path('confirm-account/', views.confirm_account, name='confirm_account'),
    path('questionnaire-interest/', views.questionnaire_interest, name='questionnaire_interest'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
    path('consent-form/', views.consent_form, name='consent_form'),

    path('waiting-screen/', views.waiting_screen, name='waiting_screen'),
    path('exit-screen-not-interested/', views.exit_screen_not_interested, name='exit_screen_not_interested'),
    path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),

    path('admin/', admin.site.urls),
]
# urlpatterns = [
#     path('', views.index, name="index"),
#     path('api/send_token_email/', views.send_token_email, name='send_token_email'),
#     path('create-account/', views.create_account, name="create_account"),  
#     path('survey/<int:survey_id>/start/', views.start_survey, name='start_survey'),
#     path('survey/<int:survey_id>/questions/', views.survey_questions, name='survey_questions'),
#     path('survey/<int:survey_id>/complete/', views.survey_complete, name='survey_complete'),
#     path('admin/', admin.site.urls),
    # path('login/', views.login_view, name='login'),  # New URL path for login
    
    # path('404', views.FourZeroFour, name="404")

    # path('', include('https://git.heroku.com/testpas.git')),
