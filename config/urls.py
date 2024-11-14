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
from testPAS import views
#import testpas.views as views
# from django.contrib.auth import views as views
app_name = 'testPAS'

urlpatterns = [
    path('', views.index, name="index"),
    path('api/send_token_email/', views.send_token_email, name='send_token_email'),
    # path('login', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='intervention/login.html'), name='login'),
    # path('logout', auth_views.LogoutView.as_view(next_page='intervention:index'), name='logout'),
    # path('profile/<int:pk>', profile_view.as_view(), name='profile'),
    # path('activate/<uidb64>/<token>', activate_account.as_view(), name='activate'),
    # path("password_reset", views.password_reset_request, name="password_reset"),
    # path('<slug:slug>', views.intervention_detail, name='intervention_detail'),
    # path('<slug:intervention_slug>/screen', views.intervention_screen_detail, name='intervention_screen_detail'),
    # path('<slug:intervention_slug>/screen/thank-you', views.intervention_screen_ineligible, name='intervention_screen_ineligible'),
    # path('<slug:intervention_slug>/screen/consent', views.intervention_screen_eligible, name='intervention_screen_eligible'),
    # path('<slug:intervention_slug>/survey/<slug:slug>', views.survey_detail, name='survey_detail'),
    # path('<slug:intervention_slug>/survey/<slug:slug>/thank-you', views.survey_detail_thank_you, name='survey_detail_thank_you'),
    # path('<slug:intervention_slug>/component/<slug:slug>', views.component_detail, name='component_detail'),
    # path('<slug:intervention_slug>/component/<slug:component_slug>/<slug:slug>', views.challenge_detail, name='challenge_detail'),
    # path('403', views.FourZeroThree, name="403"),
    path('survey/<int:survey_id>/start/', views.start_survey, name='start_survey'),
    path('survey/<int:survey_id>/questions/', views.survey_questions, name='survey_questions'),
    path('survey/<int:survey_id>/complete/', views.survey_complete, name='survey_complete'),
    path('admin/', admin.site.urls),
    # path('404', views.FourZeroFour, name="404")
]
    # # path('survey/<int:survey_id>/start/', views.start_survey, name='start_survey'),
    # # path('survey/<int:survey_id>/questions/', views.survey_questions, name='survey_questions'),
    # # path('survey/<int:survey_id>/complete/', views.survey_complete, name='survey_complete'),
    # path('admin/', admin.site.urls),
    # path('', include('config.urls')),  
    # # path('', include('testpas.views')),  
    # path('', include('https://git.heroku.com/testpas.git')),
