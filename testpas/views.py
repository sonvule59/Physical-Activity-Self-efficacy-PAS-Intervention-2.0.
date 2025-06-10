import logging
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
import json
from hashlib import sha256
from testpas.tasks import send_wave1_monitoring_email, send_wave1_code_entry_email
from testpas.settings import DEFAULT_FROM_EMAIL
# from testpas.utils import generate_token, validate_token, send_confirmation_email
from .models import *
from .utils import validate_token
import uuid
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
import os
import datetime
from twilio.rest import Client
import pytz
from .models import Participant, SurveyProgress, Survey
from .forms import CodeEntryForm, InterestForm, EligibilityForm, ConsentForm, UserRegistrationForm
import io
import csv
import zipfile
from testpas.schedule_emails import schedule_wave1_monitoring_email
from django.http import HttpResponse
from django.apps import apps
from django.db import transaction

logger = logging.getLogger(__name__)
_fake_time = None
def get_current_time():
    global _fake_time
    if _fake_time is not None:
        return _fake_time
    return timezone.now()


@login_required
def home(request):
    """Home page - shows appropriate content based on user status"""
    day_1 = 0
    if not request.user.is_authenticated:
        return render(request, 'home.html', {'user': None})
    context = {'user': request.user, 'within_wave1_period': False, 'within_wave3_period': False, 'study_day': 0}
    current_date = timezone.now().date()
    if request.user.is_authenticated:
        try:
            participant = Participant.objects.get(user=request.user)
            progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
            #  START: Correct enrollment status check
            if progress and progress.consent_given:
                context['progress'] = progress
                context['participant'] = participant
                context['start_date'] = progress.day_1
                day_1 = progress.day_1 if progress.day_1 else participant.enrollment_date if participant.enrollment_date else current_date
                study_day = (current_date - progress.day_1).days + 1 if progress.day_1 else 1
                context['study_day'] = study_day
                # context['days_until_start'] = 0
                # context['days_until_end'] = 0
                # if progress.day_1:
                    # Wave 1 code entry period (Days 11-20)
                current_date = timezone.now().date()
                # day_11 = progress.day_1 + timezone.timedelta(days=10)
                # day_21 = progress.day_1 + timezone.timedelta(days=20)
                day_11 = day_1 + timezone.timedelta(days=10)
                day_21 = day_1 + timezone.timedelta(days=20)
                context['within_wave1_period'] = day_11 <= current_date <= day_21 and not participant.code_entered
                context['days_until_start'] = (day_11 - current_date).days if current_date < day_11 else 0
                context['days_until_end'] = (day_21 - current_date).days if current_date <= day_21 else 0
                
                # Wave 3 code entry period (Days 95-104)
                day_95 = day_1 + timedelta(days=94) if progress.day_1 else current_date
                day_104 = day_1 + timedelta(days=103) if progress.day_1 else current_date
                context['within_wave3_period'] = day_95 <= current_date <= day_104 and not participant.wave3_code_entered
                context['wave3_start_date'] = day_95
                context['wave3_end_date'] = day_104
                context['wave3_days_remaining'] = (day_104 - current_date).days if day_95 <= current_date <= day_104 else 0
        
                # Intervention access
                context['show_intervention_access'] = (
                    (participant.group == 1 and 29 <= study_day <= 56) or
                    (participant.group == 0 and study_day > 112)
                    )
            else:
                context['progress'] = None  # Not enrolled
                context['participant'] = participant if participant else None
                context['study_day'] = 0
                context['within_wave1_period'] = False
                context['within_wave3_period'] = False
        except Participant.DoesNotExist:
            context['progress'] = None  # Not enrolled
            context['participant'] = None
            context['study_day'] = 0
            context['within_wave1_period'] = False
            context['within_wave3_period'] = False
            #  END
    # Calculate study day
    study_day = (current_date - day_1).days + 1
    
    # Determine what to show based on study day
    context = {
        'user': request.user,
        'participant': participant,
        'study_day': study_day,
        'within_wave1_period': False,
        'within_wave3_period': False,
    }
    
    if participant and study_day:
        # Wave 1 code entry period (Days 11-20)
        if 11 <= study_day <= 20 and not participant.code_entered:
            context['within_wave1_period'] = True
            context['wave1_start_date'] = request.user.enrollment_date + timedelta(days=10)
            context['wave1_end_date'] = request.user.enrollment_date + timedelta(days=19)
            context['wave1_days_remaining'] = 20 - study_day
        
        # Wave 3 code entry period (Days 95-104)
        elif 95 <= study_day <= 104 and not participant.wave3_code_entered:
            context['within_wave3_period'] = True
            context['wave3_start_date'] = request.user.enrollment_date + timedelta(days=94)
            context['wave3_end_date'] = request.user.enrollment_date + timedelta(days=103)
            context['wave3_days_remaining'] = 104 - study_day
        
        # Show intervention access for Group 1 during intervention period
        # if request.user.group == 1 and 29 <= study_day <= 56:
        if participant.group == 1 and 29 <= study_day <= 56:
            context['show_intervention_access'] = True
        
        # Show intervention access for Group 0 after study
        elif participant.group == 0 and study_day > 112:
            context['show_intervention_access'] = True
    
    return render(request, 'home.html', context)

# def home(request):
#     user_progress = UserSurveyProgress.objects.filter(user=request.user).first()
#     participant = Participant.objects.filter(user=request.user).first()

#     # Redirect if not eligible or consented
#     if not user_progress or not user_progress.eligible or not user_progress.consent_given or not participant:
#         return render(request, 'home.html', {
#             'user': request.user,
#             'progress': None,
#             'within_wave1_period': False,
#             'within_wave3_period': False,
#             'days_until_start': 0,
#             'days_until_end': 0,
#             'start_date': None,
#             'end_date': None
#         })

#     current_date = timezone.now()
#     try:
#         start_datetime = timezone.make_aware(
#             timezone.datetime.combine(participant.enrollment_date, timezone.datetime.min.time()),
#             timezone.get_default_timezone()
#         )
#         if settings.TEST_MODE:
#             elapsed_days = (current_date - start_datetime).total_seconds() / settings.TEST_TIME_SCALE
#         else:
#             elapsed_days = (current_date.date() - participant.enrollment_date).days
        
#         # Validate elapsed_days
#         if elapsed_days < 0 or elapsed_days > 365:
#             # logger.error(f"Invalid elapsed_days {elapsed_days} for participant {participant.participant_id}")
#             elapsed_days = 0
#     except Exception as e:
#         # logger.error(f"Error calculating elapsed_days for participant {participant.participant_id}: {e}")
#         elapsed_days = 0

#     # Wave 1: Days 11-20
#     within_wave1_period = 11 <= elapsed_days < 21 and not participant.code_entered
#     # Wave 3: Days 95-104
#     within_wave3_period = 95 <= elapsed_days < 105 and not participant.wave3_code_entered

#     context = {
#         'user': request.user,
#         'progress': participant,
#         'within_wave1_period': within_wave1_period,
#         'within_wave3_period': within_wave3_period,
#         'days_until_start': max(0, 11 - elapsed_days),
#         'days_until_end': max(0, 20 - elapsed_days) if elapsed_days < 21 else 0,
#         'start_date': participant.enrollment_date + timedelta(days=10),
#         'end_date': participant.enrollment_date + timedelta(days=20)
#     }
#     return render(request, 'home.html', context)

"""Information 2: Create Account"""
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
                    enrollment_date=timezone.now().date(),
                    is_confirmed=False
                )
                try:
                    # Use send_confirmation_email to avoid auth issues
                    participant.send_confirmation_email()
                except Exception as e:
                    logger.error(f"Failed to send account_confirmation email for participant {participant.participant_id}: {e}")
                    raise Exception(f"Email sending failed: {str(e)}")
                
                #  3: Handle AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Account created. Please check your email to confirm.',
                        'redirect': '/'
                    })
                messages.success(request, "Account created. Please check your email to confirm.")
                return redirect("home")
            except Exception as e:
                logger.error(f"Error creating account for username {form.cleaned_data.get('username')}: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Failed to create account: {str(e)}"
                    }, status=500)
                messages.error(request, "Failed to create account. Please try again.")
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please correct the errors below.',
                    'errors': form.errors
                }, status=400)
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    return render(request, "create_account.html", {'form': form})
# def create_account(request):
#     """Handle account creation with registration code"""
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Create user
#                     user = form.save(commit=False)
#                     user.registration_code = form.cleaned_data['registration_code']
#                     user.phone_number = form.cleaned_data['phone_number']
#                     user.full_name = form.cleaned_data.get('full_name', '')
#                     user.save()
                    
#                     # Create participant record
#                     participant = Participant.objects.create(
#                         user=user,
#                         participant_id=f"P{Participant.objects.count() + 1:03d}",
#                         email=user.email,
#                         confirmation_token=str(uuid.uuid4()),  # Generate token directly
#                     )
#                     # Send confirmation email (Information 3)
#                     confirmation_link = f"{settings.SITE_URL}/confirm/{participant.confirmation_token}/"
#                     participant.send_email(
#                         'account_confirmation',
#                         extra_context={
#                             'confirmation_link': confirmation_link,
#                             'username': user.username,  # Add username to context
#                         }
#                     )
#                     messages.success(
#                         request,
#                         "Account created successfully! Please check your email to activate your account."
#                     )
#                     return redirect('login')
                    
#             except Exception as e:
#                 logger.error(f"Error creating account: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#                 # Don't redirect, show the form again with error
#         else:
#             # Form is not valid, it will show errors
#             logger.error(f"Form errors: {form.errors}")
#     else:
#         form = UserRegistrationForm()
    
#     return render(request, 'create_account.html', {'form': form})

"""Information 3: Email Confirmation to Activate Account"""
# @csrf_exempt
def confirm_account(request, token):
    participant = Participant.objects.filter(confirmation_token=token).first()
    if not participant:
        messages.error(request, "Invalid or expired confirmation token.")
        return redirect("create_account")
    
    if participant.is_confirmed:
        messages.info(request, "Account already confirmed.")
    else:
        participant.is_confirmed = True
        participant.save()
        messages.success(request, "Account confirmed successfully.")
    
    return redirect("questionnaire_interest")
    # token_value = request.GET.get("token", "").strip()
    # if not token_value:
    #     return JsonResponse({"error": "Token not found."}, status=400)

    # try:
    #     token = Token.objects.get(token=token_value)
    #     user = token.recipient
    #     user.is_active = True
    #     user.save()
    #     token.used = True
    #     token.save()
    #     login(request, user)  # Auto-login after confirmation
    #     return redirect("/questionnaire/?token=" + token_value)
    # except Token.DoesNotExist:
    #     return JsonResponse({"error": "Invalid or expired token."}, status=400)
    
"""Information 3
Once participants create an account, they should be able to reset their password on the login page if they forget it."""
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')  # Redirect to next URL or dashboard
            return redirect(next_url)
            # return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    return render(request, 'login.html')

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

# @login_required
# def consent_form(request):
#     if not request.user.is_authenticated:
#         return redirect("login")

#     try:
#         participant = Participant.objects.get(user=request.user)
#     except Participant.DoesNotExist:
#         messages.error(request, "Please create a participant profile.")
#         return redirect("create_account")

#     progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
#     if not progress or not progress.eligible:
#         return redirect("exit_screen_not_eligible")

#     if request.method == "POST":
#         action = request.POST.get("action")
#         if not action and 'consent' in request.POST:
#             consent_value = request.POST.get("consent")
#             action = "consent" if consent_value == "yes" else "decline" if consent_value == "no" else None
#             logger.debug(f"Using consent parameter: {consent_value} mapped to action: {action}")

#         if not action:
#             logger.warning(f"Invalid action {action} in consent_form for {request.user.username}")
#             messages.error(request, "No valid action specified. Please select Yes or No and submit.")
#             return render(request, "consent_form.html", {"participant": participant})
#         try:
#             if action == "consent":
#                 # FIXED SNIPPET START: Handle consent action and redirect to dashboard
#                 participant.enrollment_date = timezone.now().date()
#                 participant.save()
#                 progress.consent_given = True
#                 progress.day_1 = timezone.now().date()
#                 progress.save()
#                 try:
#                     schedule_wave1_monitoring_email.delay(participant.id)
#                     logger.info(f"Scheduled wave1_monitoring_email for participant {participant.participant_id}")
#                 except Exception as e:
#                     logger.error(f"Failed to schedule wave1_monitoring_email for {participant.participant_id}: {e}")
#                     messages.error(request, "Consent saved, but email scheduling failed. Contact support.")
#                 # return redirect("dashboard")
#                 return render(request, "consent_form.html", {"participant": participant})
#                 # FIXED SNIPPET END
#             elif action == "decline":
#                 # FIXED SNIPPET START: Handle decline action and redirect to home
#                 decline_reason = request.POST.get("decline_reason", "No reason provided")
#                 progress.eligibility_reason = f"Declined consent: {decline_reason}"
#                 progress.eligible = False
#                 progress.save()
#                 logger.info(f"User {request.user.username} declined consent: {decline_reason}")
#                 messages.info(request, "You have declined to participate.")
#                 return redirect("home")
#                 # FIXED SNIPPET END
#             else:
#                 logger.warning(f"Invalid action {action} in consent_form for {request.user.username}")
#                 messages.error(request, "Invalid action. Please try again.")
#         except Exception as e:
#             logger.error(f"Error processing consent form for {request.user.username}: {e}")
#             messages.error(request, "An error occurred. Please try again or contact support.")

#     return render(request, "consent_form.html", {"participant": participant})
"""Information 6: (Website) IRB Consent Form
Participants should be able to access the IRB consent form on the website."""
@login_required
def consent_form(request):
    logger.info(f"Consent form accessed by user: {request.user.username}")
    if request.method == "POST":
        form = ConsentForm(request.POST)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            logger.info("Form is valid")
            try:
                # Update UserSurveyProgress
                # FIXED: Get or create Survey with title "Eligibility Criteria"
                survey, _ = Survey.objects.get_or_create(
                    title="Eligibility Criteria",
                    defaults={'description': "Survey for eligibility screening", 'created_at': timezone.now()}
                )
                # FIXED: Include survey in get_or_create for UserSurveyProgress
                user_progress, created = UserSurveyProgress.objects.get_or_create(
                    user=request.user,
                    survey=survey,  # ADDED: Specify survey
                    defaults={'consent_given': True, 'eligible' : True, 'day_1': timezone.now().date()}
                )
                # user_progress, created = UserSurveyProgress.objects.get_or_create(
                #     user=request.user,
                #     survey__title="Eligibility Criteria",
                #     defaults={'consent_given': True, 'day_1': timezone.now().date()}
                # )
                if not created:
                    user_progress.consent_given = True
                    user_progress.day_1 = user_progress.day_1 or timezone.now().date()
                    user_progress.eligible = True
                    user_progress.save()
                logger.info(f"UserSurveyProgress updated for {request.user.username}")

                # Get or create Participant
                participant, created = Participant.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'participant_id': f"P{Participant.objects.count() + 1:03d}",
                        'email': request.user.email,
                        'confirmation_token': str(uuid.uuid4()),
                        'enrollment_date': timezone.now().date(),
                        'is_confirmed': True,  # ADDED: Ensure confirmed
                        'engagement_tracked': True
                    }
                )
                logger.info(f"Participant record for {request.user.username}: {participant.participant_id}")

                # Send Information 9 email immediately
                participant.send_email('wave1_survey_ready')
                logger.info(f"Wave 1 survey email sent to {participant.email}")

                # Schedule Information 10 email for Day 11
                eta = timezone.now() + timedelta(seconds=55 if settings.TEST_MODE else 11 * 24 * 60 * 60)
                send_wave1_monitoring_email.apply_async(
                    args=[participant.id],
                    eta=eta
                )
                logger.info(f"Wave 1 monitoring email scheduled for {participant.participant_id} at {eta}")

                return redirect("waiting_screen")
            except Exception as e:
                logger.error(f"Error processing consent for {request.user.username}: {str(e)}", exc_info=True)
                messages.error(request, f"Error submitting consent: {str(e)}. Please try again or contact support.")
                # logger.error(f"Error processing consent for {request.user.username}: {str(e)}")
                # messages.error(request, f"An error occurred: {str(e)}")
        else:
            logger.warning(f"Form invalid for {request.user.username}: {form.errors}")
            messages.error(request, "Please correct the form errors.")
    else:
        form = ConsentForm()
        logger.debug("Rendering consent form (GET request)")
    return render(request, "consent_form.html", {'form': form})
# @login_required
# def consent_form(request):
#     if request.method == "POST":
#         form = ConsentForm(request.POST)
#         if form.is_valid():
#             user = request.user
#             user_progress = Participant.objects.get(user=user)
#             user_progress.consent_given = True
#             user_progress.save()

#             # Send Wave 1 email
#             schedule_wave1_monitoring_email(user_progress.participant_id)

#             return redirect("waiting_screen")
#     else:
#         form = ConsentForm()
#     return render(request, "consent_form.html", {'form': form})
def exit_screen_not_eligible(request):
    return render(request, 'exit_screen_not_eligible.html')

def exit_screen_declined(request):
    return render(request, 'exit_screen_declined.html')

"""DEV TIME CONTROLS"""
@login_required
def dev_time_controls(request):
    # if not request.user.is_staff:
    #     return HttpResponse("Unauthorized", status=403)
    global _fake_time
    if request.method == 'POST':
        days = int(request.POST.get('days', 0))
        _fake_time = timezone.now() + timedelta(days=days)
        return JsonResponse({'status': 'success', 'fake_time': _fake_time.isoformat()})
    return render(request, 'dev_time_controls.html')

@login_required
def dashboard(request):
    user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
    participant = Participant.objects.filter(user=request.user).first()
    current_date = get_current_time().date()
    within_wave1_period = False
    within_wave3_period = False
    days_until_start_wave1 = 0
    days_until_end_wave1 = 0
    start_date_wave1 = None
    end_date_wave1 = None
    study_day = 0
    day_11 = None
    day_21 = None
    day_95 = None
    day_104 = None
    # day_1 = progress.day_1 if progress.day_1 else participant.enrollment_date if participant.enrollment_date else current_date
    if user_progress and user_progress.eligible and user_progress.consent_given and participant:
        if not participant.enrollment_date:
            participant.enrollment_date = user_progress.day_1 or current_date
            participant.save()
        if user_progress.day_1 is not None:
            study_day = (current_date - user_progress.day_1).days + 1
            day_11 = user_progress.day_1 + timedelta(days=10)
            day_21 = user_progress.day_1 + timedelta(days=20)
            day_95 = user_progress.day_1 + timedelta(days=94)
            day_104 = user_progress.day_1 + timedelta(days=103)

            within_wave1_period = 11 <= study_day <= 20 and not participant.code_entered
            within_wave3_period = 95 <= study_day <= 104 and not participant.wave3_code_entered
            days_until_start_wave1 = max(0, (day_11 - current_date).days)
            days_until_end_wave1 = max(0, (day_21 - current_date).days)
            start_date_wave1 = day_11
            end_date_wave1 = day_21

    context = {
        'progress': user_progress,
        'participant': participant,
        'within_wave1_period': within_wave1_period,
        'within_wave3_period': within_wave3_period,
        'days_until_start_wave1': days_until_start_wave1,
        'days_until_end_wave1': days_until_end_wave1,
        'start_date_wave1': start_date_wave1,
        'end_date_wave1': end_date_wave1,
        'days_until_start_wave3': 0,
        'days_until_end_wave3': 0,
        'start_date_wave3': day_95 if user_progress else None,
        'end_date_wave3': day_104 if user_progress else None,
        'study_day': study_day if user_progress else 0  # For debugging
    }
    return render(request, "dashboard.html", context)
# @login_required
# def dashboard(request):
#     """Dashboard page - shows user progress and study status"""
#     #  Wave 1 period calculation and remaining days
#     context = {
#         'user': request.user,
#         'within_wave1_period': False,
#         'within_wave3_period': False,
#         'study_day': 0
#     }
#     current_date = timezone.now().date()

#     user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
#     if user_progress and user_progress.eligible and user_progress.consent_given:
#         participant, created = Participant.objects.get_or_create(
#             user=request.user,
#             defaults={
#                 #  1: Use day_1 for enrollment_date
#                 'enrollment_date': user_progress.day_1 if user_progress.day_1 else timezone.now().date(),
#                 'code_entered': False,
#                 'age': 30,
#                 'confirmation_token': str(uuid.uuid4()),
#                 'participant_id': f"P{Participant.objects.count() + 1:03d}",
#                 'email': request.user.email
#             }
#         )
#         #  2: Update survey completion and progress percentage
#         if created or not user_progress.survey_completed:
#             try:
#                 survey = Survey.objects.get(title="Eligibility Criteria")
#                 total_questions = survey.questions.count()
#                 answered_questions = Response.objects.filter(user=request.user, question__survey=survey).count()
#                 if answered_questions >= total_questions:
#                     user_progress.survey_completed = True
#                     user_progress.progress_percentage = 100
#                 else:
#                     user_progress.survey_completed = False
#                     user_progress.progress_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
#                 user_progress.save()
#             except Survey.DoesNotExist:
#                 logger.error("Eligibility survey not found for user %s", request.user.username)
#                 user_progress.survey_completed = False
#                 user_progress.progress_percentage = 0
#                 user_progress.save()
#         # Ensure day_1 is set
#         if not user_progress.day_1:
#             user_progress.day_1 = participant.enrollment_date
#             user_progress.save()
#         context['participant'] = participant
#         context['progress'] = user_progress
#     else:
#         participant = None
#         context['participant'] = None
#         context['progress'] = None

#     #  3: Use day_1 for Wave 1 period calculation
#     if user_progress and user_progress.day_1:
#         day_1 = user_progress.day_1
#         study_day = (current_date - day_1).days + 1
#         context['study_day'] = study_day
#         day_11 = day_1 + timedelta(days=10)
#         day_21 = day_1 + timedelta(days=20)
#         context['within_wave1_period'] = day_11 <= current_date <= day_21 and participant and not participant.code_entered
#         context['days_until_start_wave1'] = max((day_11 - current_date).days, 0)
#         context['days_until_end_wave1'] = max((day_21 - current_date).days, 0) if context['within_wave1_period'] else 0
#         context['start_date_wave1'] = day_11
#         context['end_date_wave1'] = day_21

#         day_95 = day_1 + timedelta(days=94)
#         day_104 = day_1 + timedelta(days=103)
#         context['within_wave3_period'] = day_95 <= current_date <= day_104 and participant and not participant.wave3_code_entered
#         context['days_until_start_wave3'] = max((day_95 - current_date).days, 0)
#         context['days_until_end_wave3'] = max((day_104 - current_date).days, 0) if context['within_wave3_period'] else 0
#         context['start_date_wave3'] = day_95
#         context['end_date_wave3'] = day_104

#     return render(request, 'dashboard.html', context)
# def dashboard(request):
#     user_progress = UserSurveyProgress.objects.filter(user=request.user).first()
#     if user_progress and user_progress.eligible and user_progress.consent_given:
#         participant, created = Participant.objects.get_or_create(
#             user=request.user,
#             defaults={
#                 # Preserve existing enrollment_date if participant exists
#                 'enrollment_date': user_progress.day_1 if user_progress.day_1 else timezone.now().date(),
#                 'code_entered': False,
#                 'age': 30,
#                 'confirmation_token': str(uuid.uuid4()),
#                 'participant_id': f"P{Participant.objects.count() + 1:03d}",
#                 'email': request.user.email
#             }
#         )
#         # Update survey completion and progress percentage
#         # if created or not user_progress.survey_completed:
#         #     user_progress.survey_completed= True
#         #     user_progress.progress_percentage = 100
#         #     user_progress.save()
#         #  START: Set survey completion and progress percentage only when survey is done
#         if created or not user_progress.survey_completed:
#             try:
#                 survey = Survey.objects.get(title="Eligibility Criteria")
#                 total_questions = survey.questions.count()
#                 answered_questions = Response.objects.filter(user=request.user, question__survey=survey).count()
#                 if answered_questions >= total_questions:
#                     user_progress.survey_completed = True
#                     user_progress.progress_percentage = 100
#                 else:
#                     user_progress.survey_completed = False
#                     user_progress.progress_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
#                 user_progress.save()
#             except Survey.DoesNotExist:
#                 logger.error("Eligibility survey not found for user %s", request.user.username)
#                 user_progress.survey_completed = False
#                 user_progress.progress_percentage = 0
#                 user_progress.save()
#     else:
#         participant = None
    
#     current_date = timezone.now().date()
#     # Calculate wave periods based on enrollment date
#     # NOTE: Use user_progress.day_1 if available, otherwise use current date
#     day_11 = (user_progress.day_1 + timedelta(days=10)) if user_progress and user_progress.day_1 else current_date
#     day_21 = (user_progress.day_1 + timedelta(days=20)) if user_progress and user_progress.day_1 else current_date
#     day_95 = (user_progress.day_1 + timedelta(days=94)) if user_progress and user_progress.day_1 else current_date
#     day_104 = (user_progress.day_1 + timedelta(days=103)) if user_progress and user_progress.day_1 else current_date
#     within_wave1_period = day_11 <= current_date <= day_21 if user_progress else False
#     within_wave3_period = day_95 <= current_date <= day_104 if user_progress else False
#     # current_date = timezone.now().date()
#     # day_11 = participant.enrollment_date + timedelta(days=10) if participant else current_date
#     # day_21 = participant.enrollment_date + timedelta(days=20) if participant else current_date
#     # day_95 = participant.enrollment_date + timedelta(days=94) if participant else current_date
#     # day_104 = participant.enrollment_date + timedelta(days=103) if participant else current_date
#     # within_wave1_period = day_11 <= current_date <= day_21 if participant else False
#     # within_wave3_period = day_95 <= current_date <= day_104 if participant else False
#     context = {
#         'progress': user_progress,
#         'participant': participant,
#         'within_wave1_period': within_wave1_period,
#         'within_wave3_period': within_wave3_period,
#         'days_until_start_wave1': (day_11 - current_date).days if current_date < day_11 else 0,
#         'days_until_end_wave1': (day_21 - current_date).days if current_date <= day_21 else 0,
#         'start_date_wave1': day_11,
#         'end_date_wave1': day_21,
#         'days_until_start_wave3': (day_95 - current_date).days if current_date < day_95 else 0,
#         'days_until_end_wave3': (day_104 - current_date).days if current_date <= day_104 else 0,
#         'start_date_wave3': day_95,
#         'end_date_wave3': day_104
#     }
#     return render(request, "dashboard.html", context)

# INFORMATION 11 & 22: Enter Code
@login_required
def enter_code(request, wave):
    """Handle code entry for Wave 1 or Wave 3"""
    participant = get_object_or_404(Participant, user=request.user)
    user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
    if not user_progress or not user_progress.day_1:
        messages.error(request, "Enrollment date not set. Contact support.")
        return redirect('home')
    # if not user_progress:
    #     messages.error(request, "No progress recorded. Contact support.")
    #     return redirect('home')
    # if not user_progress.day_1:
    #     user_progress.day_1 = participant.enrollment_date if participant.enrollment_date else timezone.now().date()
    #     user_progress.save()
    # current_date = timezone.now().date()
    # study_day = (current_date - user_progress.day_1).days + 1
    # if user_progress and user_progress.day_1:
    #     current_date = timezone.now().date()
    #     study_day = (current_date - user_progress.day_1).days + 1
    # else:
    #     messages.error(request, "Enrollment date not set. Contact support.")
    #     return redirect('home')
    current_date = timezone.now().date()
    study_day = (current_date - user_progress.day_1).days + 1
    if wave == 1:
        # Check if within Wave 1 window (Days 11-20)
        if not (11 <= study_day <= 20):
            messages.error(request, "Code entry is not available at this time.")
            return redirect('home')
        if participant.code_entered:
            messages.info(request, "You have already entered the code for Wave 1.")
            return redirect('home')
            
    elif wave == 3:
        # Check if within Wave 3 window (Days 95-104)
        if not (95 <= study_day <= 104):
            messages.error(request, "Code entry is not available at this time.")
            return redirect('home')
        if participant.wave3_code_entered:
            messages.info(request, "You have already entered the code for Wave 3.")
            return redirect('home')
    
    if request.method == 'POST':
        form = CodeEntryForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].strip().lower()
            
            # if code == settings.REGISTRATION_CODE.lower():
            if code == 'wavepa':
                if wave == 1:
                    participant.code_entered = True
                    participant.code_entry_date = timezone.now().date()
                    participant.save()
                    send_wave1_code_entry_email.delay(participant.id)
                    messages.success(request, "Code entered successfully!")
                    return redirect('code_success', wave=wave)
                    # participant.code_entered = True
                    # participant.code_entry_date = timezone.now().date()
                    # participant.save()
                    
                    # Send Information 12 email
                    # send_wave1_code_entry_email.delay(participant.id)
                    
                elif wave == 3:
                    participant.wave3_code_entered = True
                    participant.wave3_code_entry_date = timezone.now().date()
                    participant.save()
                    # send_wave3_code_entry_email.delay(participant.id)
                    messages.success(request, "Code entered successfully!")
                    return redirect('code_success', wave=wave)
                
                messages.success(request, "Code entered successfully!")
                return redirect('code_success', wave=wave)
            else:
                messages.error(request, "Incorrect code. Please try again.")
    else:
        form = CodeEntryForm()
    
    context = {
        'form': form,
        'wave': wave,
        'days_remaining': 20 - study_day if wave == 1 else 104 - study_day,
    }
    
    return render(request, 'monitoring/enter_code.html', context)
# @login_required
# def enter_code(request):
#     participant = Participant.objects.get(user=request.user)
#     current_date = timezone.now().date()

#     day_11 = participant.enrollment_date + timedelta(days=10)
#     day_21 = participant.enrollment_date + timedelta(days=20)

#     if current_date < day_11:
#         messages.error(request, "You cannot enter the code before Day 11.")
#         return redirect('home')

#     if current_date > day_21:
#         messages.error(request, "The time window for entering the code has passed.")
#         return redirect('home')

#     if request.method == 'POST':
#         form = CodeEntryForm(request.POST)
#         if form.is_valid():
#             code = form.cleaned_data['code'].strip().lower()
#             if code == 'wavepa':
#                 participant.code_entered = True
#                 participant.code_entry_date = current_date
#                 participant.save()
#                 participant.send_code_entry_email()
#                 messages.success(request, "Code entered successfully!")
#                 return redirect('code_success')
#             else:
#                 messages.error(request, "Incorrect code. Please try again.")
#     else:
#         form = CodeEntryForm()

#     return render(request, 'enter_code.html', {
#         'form': form,
#         'days_remaining': (day_21 - current_date).days
#     })

def code_success(request, wave):
    return render(request, 'code_success.html', {'wave': wave})
    # participant = Participant.objects.get(user=request.user)
    # current_date = timezone.now().date()
    # day_21 = participant.enrollment_date + timedelta(days=20)
    # days_remaining = (day_21 - current_date).days
    # return render(request, 'code_success.html', {'days_remaining': days_remaining})

def code_failure(request):
    participant = Participant.objects.get(user=request.user)
    current_date = timezone.now().date()
    day_21 = participant.enrollment_date + timedelta(days=20)
    days_remaining = (day_21 - current_date).days
    return render(request, 'code_failure.html', {'days_remaining': days_remaining})

def exit_screen_not_interested(request):
    if request.method == 'GET':
        return render(request, 'exit_screen_not_interested.html')
def waiting_screen(request):
    return render(request, "waiting_screen.html")

def logout_view(request):
    logout (request)
    return redirect('login')  # Redirect to the login page after logout
