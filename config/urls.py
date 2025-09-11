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
from testpas.views import *

urlpatterns = [
    # Landing page and authentication
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Information 2: Create Account
    path('create-account/', views.create_account, name='create_account'),
    path('create-participant/', views.create_account, name='create_participant'),  # Alias for compatibility
    
    # Information 3: Email Confirmation
    path('confirm/<str:token>/', views.confirm_account, name='confirm_account'),
    path('confirm-account/<str:token>/', views.confirm_account, name='confirm_account_alt'),  # Alias
    
    # Questionnaire flow
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    
    # Information 4: Interest Screening
    path('questionnaire/interest/', views.questionnaire_interest, name='questionnaire_interest'),  # type: ignore
    
    # Information 6: Consent Form
    path('questionnaire/consent/', views.consent_form, name='consent_form'),
    # path('consent/download/', views.download_consent, name='download_consent'),
    
    # Information 7: Exit Screens
    # path('exit/not-interested/', views.exit_not_interested, name='exit_not_interested'),
    path('exit/not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),

    
    # Information 8: Waiting Screen
    path('waiting_screen/', views.waiting_screen, name='waiting_screen'),
    
    # Information 11 & 22: Code Entry
    path('enter-code/<int:wave>/', views.enter_code, name='enter_code'),
    path('enter-wave3-code/', views.enter_code, {'wave': 3}, name='enter_wave3_code'),
    path('code-success/<int:wave>/', views.code_success, name='code_success'),
    path('code-failure/', views.code_failure, name='code_failure'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('intervention/', views.intervention_access, name='intervention_access'),
    path('intervention/test/', views.intervention_access_test, name='intervention_access_test'),
    path('intervention/challenge-25/', views.intervention_challenge_25, name='intervention_challenge_25'),
    path('dev/time-controls/', views.dev_time_controls, name='dev_time_controls'),
    
    # Surveys (Information 9, 18, 20)
    path('survey/wave<int:wave>/', views.survey_view, name='survey'),
    
    # Daily Activity Logs (Information 13, 24)
    path('survey/daily-log/wave<int:wave>/', views.daily_log_view, name='daily_log'),
]

# app_name = 'testpas'
# urlpatterns = [
#     path('', views.home, name='home'),  # Home page
#     path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
#     path('enter-code/', views.enter_code, name='enter_code'),
#     path('code-success/', views.code_success, name='code_success'),
#     path('code-failure/', views.code_failure, name='code_failure'),
    
#     path('', views.questionnaire_interest, name="index"),
#     path('create-account/', views.create_account, name='create_account'),
#     path('confirm-account/', views.confirm_account, name='confirm_account'),
#     path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # Default Django login view
#     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # Default Django logout view
#     path('login/', views.login_view, name='login'),
#     # path('login-with-token/', views.login_with_token, name='login_with_token'),
#     path('logout/', views.logout_view, name='logout'),
#     path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('confirm-account/', views.confirm_account, name='confirm_account'),
    
#     path('questionnaire-interest/', views.questionnaire_interest, name='questionnaire_interest'),
#     path('questionnaire/', views.questionnaire, name='questionnaire'), 
#     path('consent-form/', views.consent_form, name='consent_form'),
#     # path('waiting-screen/', views.waiting_screen, name='waiting_screen'),
#     path('exit-screen-not-interested/', views.exit_screen_not_interested, name='exit_screen_not_interested'),
#     # path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
#     # path('send_scheduled_email/', views.send_scheduled_email, name='send_scheduled_email'),
#     # path('enter-wave-3-code/', views.enter_wave_3_code, name='enter_wave3_code'),
#     path('enter-code/', views.enter_code, name='enter_code'),
#     # path('check-day-21/', views.check_day_21, name='check_day_21'),
#     path('code-success/', views.code_success, name='code_success'),
#     path('code-failure/', views.code_failure, name='code_failure'),
#     path('admin/', admin.site.urls),
    
#     # The line `path('', include('config.urls'))` is including the URL patterns defined in the
#     # `config.urls` module into the main URL configuration of the `testPAS` project. This allows you
#     # to organize your URL patterns into separate modules for better code organization and
#     # maintainability. By including `config.urls`, you can define additional URL patterns specific to
#     # the `config` app without cluttering the main `urlpatterns` list in this file.
#     # path('', include('config.urls'))
#     # path('', views.questionnaire_interest, name="index"),
#     # path('create-account/', views.create_account, name='create_account'),
#     # path('confirm-account/', views.confirm_account, name='confirm_account'),
#     # path('questionnaire-interest/', views.questionnaire_interest, name='questionnaire_interest'),
#     # path('questionnaire/', views.questionnaire, name='questionnaire'),
#     # path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
#     # path('consent-form/', views.consent_form, name='consent_form'),

#     # path('waiting-screen/', views.waiting_screen, name='waiting_screen'),
#     # path('exit-screen-not-interested/', views.exit_screen_not_interested, name='exit_screen_not_interested'),
#     # path('exit-screen-not-eligible/', views.exit_screen_not_eligible, name='exit_screen_not_eligible'),
#     # path('questionnaire/', views.questionnaire, name='questionnaire'),  # Add this line for questionnaire
#     # path('confirm-account/', views.confirm_account, name='confirm_account'),
    
#     # path('admin/', admin.site.urls),
# ]

# # if settings.DEBUG:
# #     urlpatterns += [
# #         path('dev/time-controls/', views.dev_time_controls, name='dev_time_controls'),
# #     ]
