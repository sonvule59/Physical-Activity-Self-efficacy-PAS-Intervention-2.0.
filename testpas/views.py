from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.crypto import get_random_string
import json
from hashlib import sha256
from .settings import *
from .models import *
from .utils import validate_token
import uuid
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from freezegun import freeze_time
import os
import datetime
# from twilio.rest import Client
import pytz
from .models import Participant
import requests
from .forms import CodeEntryForm, ConsentForm, EligibilityForm
# from .tasks.tasks import send_scheduled_email

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from testpas.models import User, Token, UserSurveyProgress
from django.conf import settings
from .forms import UserRegistrationForm

def create_account(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                participant = Participant.objects.create(
                    user=user,
                    email=user.email,
                    phone_number=form.cleaned_data['phone_number'],
                    confirmation_token=str(uuid.uuid4()),
                    participant_id=f"P{Participant.objects.count():03d}",
                    enrollment_date=timezone.now().date()
                )
                # Send confirmation email
                confirmation_link = f"{settings.BASE_URL}/confirm-account/{participant.confirmation_token}/"
                participant.send_email(
                    'account_confirmation',
                    extra_context={'confirmation_link': confirmation_link},
                    mark_as='sent_confirmation'
                )
                messages.success(request, "Account created. Please check your email to confirm.")
                return redirect("home")
            except Exception as e:
                messages.error(request, "Failed to create account. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, "create_account.html", {'form': form})
# def create_account(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         email = request.POST.get('email')
#         # Create a new user
#         user = User.objects.create_user(username=username, password=password, email=email)
#         token = Token.objects.create(receipient=user)
#         user.save()
#         # Send confirmation email
#         confirmation_url = f"{request.build_absolute_uri('/confirm-account/')}?token={token.token}"
#         send_mail(
#             "Confirm Your Account",
#             f"Click the link to confirm your account: {confirmation_url}",
#             "vuleson59@gmail.com",
#             [user.email], [token.token]
#         )
#         return redirect('login')  # Redirect to the login page after account creation
#     return render(request, 'create_account.html')

# 2️⃣ Confirm Account
def confirm_account(request):
    token_value = request.GET.get("token", "").strip()
    if not token_value:
        return JsonResponse({"error": "Token not found."}, status=400)

    try:
        token = Token.objects.get(token=token_value)
        user = token.recipient
        user.is_active = True
        user.save()
        token.used = True
        token.save()
        login(request, user)  # Auto-login after confirmation
        return redirect("/questionnaire/?token=" + token_value)
    except Token.DoesNotExist:
        return JsonResponse({"error": "Invalid or expired token."}, status=400)

def questionnaire_interest(request):
    if request.method == 'GET':
        return render(request, 'questionnaire_interest.html')
    elif request.method == 'POST':
        interested = request.POST.get('interested')
        if interested == 'no':
            return redirect('exit_screen_not_interested')
        return redirect('questionnaire')

## Create Membership
def create_participant(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number").strip()

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        # Create User only
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({"message": "User registered successfully! Please complete the eligibility questionnaire."})
    return render(request, "create_participant.html")

@login_required
def questionnaire(request):
    if request.method == "POST":
        user = request.user
        answers = request.POST
        print(f"Full POST Data: {answers}")

        age = int(answers.get("age", 0))
        height = int(answers.get("height", 0))
        weight = int(answers.get("weight", 0))
        access_to_device = answers.get("has_device", "").strip().lower() == "yes"
        willing_no_other_study = answers.get("not_enroll_other", "").strip().lower() == "yes"
        willing_monitor = answers.get("comply_monitoring", "").strip().lower() == "yes"
        willing_contact = answers.get("respond_contacts", "").strip().lower() == "yes"
        bmi = (weight / (height ** 2)) * 703 if height > 0 else 0

        print(f"Age: {age}, BMI: {bmi:.2f}, Device: {access_to_device}, No Other Study: {willing_no_other_study}")
        print(f"Monitor: {willing_monitor}, Contact: {willing_contact}")

        eligible = (
            (18 <= age <= 64) and
            (bmi >= 25) and
            access_to_device and
            willing_no_other_study and
            willing_monitor and
            willing_contact
        )
        print(f"Eligibility Result: {eligible}")

        survey = Survey.objects.first()
        if not survey:
            return JsonResponse({"error": "No survey available. Contact support."}, status=500)

        user_progress, created = UserSurveyProgress.objects.get_or_create(
            user=user,
            survey=survey,
            defaults={'eligible': eligible, 'consent_given': False}
        )
        if not created:
            user_progress.eligible = eligible
            user_progress.save()

        if eligible:
            return redirect("consent_form")
        else:
            return redirect(reverse("exit_screen_not_eligible"))
    return render(request, "questionnaire.html")
def send_wave_1_email(user):
    subject = "Wave 1 Online Survey Set – Ready"
    message = f"""
    Hi {user.username},

    Congratulations! You are now enrolled as a participant in the study.

    Your next task is to complete the Wave 1 Online Survey Set within 10 days. 
    Please check your email for further details.

    Best,  
    The Research Team
    """
    from_email = "vuleson59@gmail.com" 
    recipient_list = [user.email, "vuleson59@gmail.com"] 

    send_mail(subject, message, from_email, recipient_list)

@login_required
def consent_form(request):
    if request.method == "POST":
        form = ConsentForm(request.POST)
        if form.is_valid():
            user = request.user
            user_progress = UserSurveyProgress.objects.get(user=user)
            user_progress.consent_given = True
            user_progress.save()

            # Send Wave 1 email
            send_wave_1_email(user)

            return redirect("waiting_screen")
    else:
        form = ConsentForm()
    return render(request, "consent_form.html", {'form': form})

@login_required
def home(request):
    user_progress = UserSurveyProgress.objects.filter(user=request.user).first()
    participant = Participant.objects.filter(user=request.user).first()

    # Redirect if not eligible or consented
    if not user_progress or not user_progress.eligible or not user_progress.consent_given or not participant:
        return render(request, 'home.html', {
            'user': request.user,
            'progress': None,
            'within_wave1_period': False,
            'within_wave3_period': False,
            'days_until_start': 0,
            'days_until_end': 0,
            'start_date': None,
            'end_date': None
        })

    current_date = timezone.now()
    try:
        start_datetime = timezone.make_aware(
            timezone.datetime.combine(participant.enrollment_date, timezone.datetime.min.time()),
            timezone.get_default_timezone()
        )
        if settings.TEST_MODE:
            elapsed_days = (current_date - start_datetime).total_seconds() / settings.TEST_TIME_SCALE
        else:
            elapsed_days = (current_date.date() - participant.enrollment_date).days
        
        # Validate elapsed_days
        if elapsed_days < 0 or elapsed_days > 365:
            # logger.error(f"Invalid elapsed_days {elapsed_days} for participant {participant.participant_id}")
            elapsed_days = 0
    except Exception as e:
        # logger.error(f"Error calculating elapsed_days for participant {participant.participant_id}: {e}")
        elapsed_days = 0

    # Wave 1: Days 11-20
    within_wave1_period = 11 <= elapsed_days < 21 and not participant.code_entered
    # Wave 3: Days 95-104
    within_wave3_period = 95 <= elapsed_days < 105 and not participant.wave3_code_entered

    context = {
        'user': request.user,
        'progress': participant,
        'within_wave1_period': within_wave1_period,
        'within_wave3_period': within_wave3_period,
        'days_until_start': max(0, 11 - elapsed_days),
        'days_until_end': max(0, 20 - elapsed_days) if elapsed_days < 21 else 0,
        'start_date': participant.enrollment_date + timedelta(days=10),
        'end_date': participant.enrollment_date + timedelta(days=20)
    }
    # logger.debug(f"Rendering home.html with within_wave1_period={within_wave1_period}, within_wave3_period={within_wave3_period}, elapsed_days={elapsed_days}")
    return render(request, 'home.html', context)
@login_required
def dashboard(request):
    user_progress = UserSurveyProgress.objects.filter(user=request.user).first()
    if user_progress and user_progress.eligible and user_progress.consent_given:
        participant, created = Participant.objects.get_or_create(
            user=request.user,
            defaults={
                'enrollment_date': timezone.now().date(),
                'code_entered': False,
                'age': 30,
                'confirmation_token': str(uuid.uuid4()),
                'participant_id': f"P{Participant.objects.count() + 1:03d}",
                'email': request.user.email
            }
        )
    else:
        participant = None
    current_date = timezone.now().date()
    day_11 = participant.enrollment_date + timedelta(days=10) if participant else current_date
    day_21 = participant.enrollment_date + timedelta(days=20) if participant else current_date
    day_95 = participant.enrollment_date + timedelta(days=94) if participant else current_date
    day_104 = participant.enrollment_date + timedelta(days=103) if participant else current_date
    within_wave1_period = day_11 <= current_date <= day_21 if participant else False
    within_wave3_period = day_95 <= current_date <= day_104 if participant else False
    context = {
        'progress': user_progress,
        'participant': participant,
        'within_wave1_period': within_wave1_period,
        'within_wave3_period': within_wave3_period,
        'days_until_start_wave1': (day_11 - current_date).days if current_date < day_11 else 0,
        'days_until_end_wave1': (day_21 - current_date).days if current_date <= day_21 else 0,
        'start_date_wave1': day_11,
        'end_date_wave1': day_21,
        'days_until_start_wave3': (day_95 - current_date).days if current_date < day_95 else 0,
        'days_until_end_wave3': (day_104 - current_date).days if current_date <= day_104 else 0,
        'start_date_wave3': day_95,
        'end_date_wave3': day_104
    }
    return render(request, "dashboard.html", context)


def exit_screen_not_interested(request):
    if request.method == 'GET':
        return render(request, 'exit_screen_not_interested.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout (request)
    return redirect('login')  # Redirect to the login page after logout
