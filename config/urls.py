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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from testpas import views, settings
from testpas.views import send_scheduled_email

app_name = 'testpas'
urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
    path('enter-code/', views.enter_code, name='enter_code'),
    path('code-success/', views.code_success, name='code_success'),
    path('code-failure/', views.code_failure, name='code_failure'),
    path('check-day-21/', views.check_day_21, name='check_day_21'),
    # path('', views.questionnaire_interest, name="index"),
    path('create-account/', views.create_account, name='create_account'),
    path('confirm-account/', views.confirm_account, name='confirm_account'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # Default Django login view
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # Default Django logout view
    path('login/', views.login_view, name='login'),
    path('login-with-token/', views.login_with_token, name='login_with_token'),
    # path('logout/', views.logout_view, name='logout'),
     path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('confirm-account/', views.confirm_account, name='confirm_account'),
    path('questionnaire-interest/', views.questionnaire_interest, name='questionnaire_interest'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
    path('consent-form/', views.consent_form, name='consent_form'),
    path('waiting-screen/', views.waiting_screen, name='waiting_screen'),
    path('exit-screen-not-interested/', views.exit_screen_not_interested, name='exit_screen_not_interested'),
    path('send_scheduled_email/', send_scheduled_email, name='send_scheduled_email'),

    # path('enter-code/', views.enter_code, name='enter_code'),
    # path('check-day-21/', views.check_day_21, name='check_day_21'),
    # path('code-success/', views.code_success, name='code_success'),
    # path('code-failure/', views.code_failure, name='code_failure'),
    path('admin/', admin.site.urls),
    # path('', views.questionnaire_interest, name="index"),
    # path('create-account/', views.create_account, name='create_account'),
    # path('confirm-account/', views.confirm_account, name='confirm_account'),
    # path('questionnaire-interest/', views.questionnaire_interest, name='questionnaire_interest'),
    # path('questionnaire/', views.questionnaire, name='questionnaire'),
    # path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
    # path('consent-form/', views.consent_form, name='consent_form'),

    # path('waiting-screen/', views.waiting_screen, name='waiting_screen'),
    # path('exit-screen-not-interested/', views.exit_screen_not_interested, name='exit_screen_not_interested'),
    # path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
    # path('questionnaire/', views.questionnaire, name='questionnaire'),  # Add this line for questionnaire
    # path('confirm-account/', views.confirm_account, name='confirm_account'),
    
    # path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path('dev/time-controls/', views.dev_time_controls, name='dev_time_controls'),
    ]


    # path('', include('https://git.heroku.com/testpas.git')),
