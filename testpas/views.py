# type: ignore
from bz2 import compress
import logging
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from hashlib import sha256
from testpas.tasks import send_wave1_monitoring_email, send_wave1_code_entry_email, send_wave3_code_entry_email
# from testpas.settings import DEFAULT_FROM_EMAIL
from testpas.schedule_emails import schedule_wave1_monitoring_email
# from testpas.utils import generate_token, validate_token, send_confirmation_email
from .models import *
from .utils import validate_token
import uuid
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from testpas.settings import *
import os
import datetime
from twilio.rest import Client
import pytz
from .models import Participant, SurveyProgress, Survey, UserSurveyProgress, Content
from django.db.models import Model
from .forms import CodeEntryForm, InterestForm, EligibilityForm, ConsentForm, UserRegistrationForm, PasswordResetForm, PasswordResetConfirmForm
import csv
from testpas.schedule_emails import schedule_wave1_monitoring_email
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from testpas.utils import get_current_time

from .timeline import get_timeline_day, get_study_day
from django.conf import settings

logger = logging.getLogger(__name__)

def landing(request):
    """Landing page for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

@login_required
def home(request):

# current_date = timezone.now().date()
#     day_1 = current_date  # Initialize with current_date instead of 0
#     participant = None  # Initialize participant
#     if not request.user.is_authenticated:
#         return render(request, 'home.html', {'user': None})
#     context = {'user': request.user, 'within_wave1_period': False, 'within_wave3_period': False, 'study_day': 0}
#     current_date = timezone.now().date()
#     if request.user.is_authenticated:
#         try:
#             participant = Participant.objects.get(user=request.user)
#             progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
#             #  START: Correct enrollment status check
#             if progress and progress.consent_given:
#                 context['progress'] = progress
#                 context['participant'] = participant
#                 context['start_date'] = progress.day_1
#                 day_1 = progress.day_1 if progress.day_1 else participant.enrollment_date if participant.enrollment_date else current_date
#                 # study_day = (current_date - progress.day_1).days + 1 if progress.day_1 else 1
#                 # Use compressed timeline calculation
#                 study_day = get_study_day(
#                     progress.day_1,
#                     now=get_current_time(),
#                     compressed=settings.TIME_COMPRESSION,   
#                     seconds_per_day=settings.SECONDS_PER_DAY
#                 ) if progress.day_1 else 1
#                 context['study_day'] = study_day
#                 # context['days_until_start'] = 0
#                 # context['days_until_end'] = 0
#                 # if progress.day_1:
#                     # Wave 1 code entry period (Days 11-20)
#                 current_date = timezone.now().date()
#                 # day_11 = progress.day_1 + timezone.timedelta(days=10)
#                 # day_21 = progress.day_1 + timezone.timedelta(days=20)
#                 day_11 = day_1 + timezone.timedelta(days=10)
#                 day_21 = day_1 + timezone.timedelta(days=20)
#                 context['within_wave1_period'] = day_11 <= current_date <= day_21 and not participant.code_entered
#                 context['days_until_start'] = (day_11 - current_date).days if current_date < day_11 else 0
#                 context['days_until_end'] = (day_21 - current_date).days if current_date <= day_21 else 0
                
#                 # Wave 3 code entry period (Days 95-104)
#                 day_95 = day_1 + timedelta(days=94) if progress.day_1 else current_date
#                 day_104 = day_1 + timedelta(days=103) if progress.day_1 else current_date
#                 context['within_wave3_period'] = day_95 <= current_date <= day_104 and not participant.wave3_code_entered
#                 context['wave3_start_date'] = day_95
#                 context['wave3_end_date'] = day_104
#                 context['wave3_days_remaining'] = (day_104 - current_date).days if day_95 <= current_date <= day_104 else 0
        
#                 # Intervention access
#                 context['show_intervention_access'] = (
#                     (participant.group == 1 and 29 <= study_day <= 56) or
#                     (participant.group == 0 and study_day > 112)
#                     )
#             else:
#                 context['progress'] = None  # Not enrolled
#                 context['participant'] = participant if participant else None
#                 context['study_day'] = 0
#                 context['within_wave1_period'] = False
#                 context['within_wave3_period'] = False
#         except Participant.DoesNotExist:
#             context['progress'] = None  # Not enrolled
#             context['participant'] = None
#             context['study_day'] = 0
#             context['within_wave1_period'] = False
#             context['within_wave3_period'] = False
#             #  END
#     # Calculate study day
#     study_day = (current_date - day_1).days + 1
    
#     # Determine what to show based on study day
#     context = {
#         'user': request.user,
#         'participant': participant,
#         'study_day': study_day,
#         'within_wave1_period': False,
#         'within_wave3_period': False,
#     }
    
#     if participant and study_day:
#         # Wave 1 code entry period (Days 11-20)
#         if 11 <= study_day <= 20 and not participant.code_entered:
#             context['within_wave1_period'] = True
#             context['wave1_start_date'] = participant.enrollment_date + timedelta(days=10)
#             context['wave1_end_date'] = participant.enrollment_date + timedelta(days=19)
#             context['wave1_days_remaining'] = 20 - study_day
        
#         # Wave 3 code entry period (Days 95-104)
#         elif 95 <= study_day <= 104 and not participant.wave3_code_entered:
#             context['within_wave3_period'] = True
#             context['wave3_start_date'] = participant.enrollment_date + timedelta(days=94)
#             context['wave3_end_date'] = participant.enrollment_date + timedelta(days=103)
#             context['wave3_days_remaining'] = 104 - study_day
        
#         if participant.group == 1 and 29 <= study_day <= 56:
#             context['show_intervention_access'] = True
        
#         # Show intervention access for Group 0 after study
#         elif participant.group == 0 and study_day > 112:
#             context['show_intervention_access'] = True
    
#     return render(request, 'home.html', context)
    """Home page - redirects authenticated users to dashboard"""
    return redirect('dashboard')


"""Information 2: Create Account"""
def create_account(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Clear any existing session data to prevent user confusion
                request.session.flush()
                
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
                return redirect("landing")
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

"""Information 3: Email Confirmation to Activate Account"""
@csrf_exempt
def confirm_account(request, token):
    participant = Participant.objects.filter(confirmation_token=token).first()
    if not participant:
        messages.error(request, "Invalid or expired confirmation token.")
        return redirect("create_account")
    print(f"[DEBUG] Participant found: {participant.participant_id}")
    print(f"[DEBUG] Participant is confirmed: {participant.is_confirmed}")
    if participant.is_confirmed:
        messages.info(request, "Account already confirmed.")
    else:
        participant.is_confirmed = True
        participant.save()
        messages.success(request, "Account confirmed successfully.")
    
    return redirect("questionnaire_interest")

    
"""Information 3
Once participants create an account, they should be able to reset their password on the login page if they forget it."""
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"[DEBUG] Login attempt for username: {username}")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"[DEBUG] Authentication successful for user: {user.username}")
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')  # Redirect to next URL or dashboard
            print(f"[DEBUG] Redirecting to: {next_url}")
            return redirect(next_url)
            # return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            print(f"[DEBUG] Authentication failed for username: {username}")
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    return render(request, 'login.html')

def password_reset(request):
    """Handle password reset request"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate reset token
                token = Token.generate_token()
                Token.objects.create(recipient=user, token=token)
                
                # Send reset email
                reset_link = f"{settings.BASE_URL}/password-reset-confirm/{token}/"
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_link}\n\nIf you did not request this, please ignore this email.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset email sent. Please check your email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No user found with that email address.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form})

def password_reset_confirm(request, token):
    """Handle password reset confirmation"""
    try:
        token_obj = Token.objects.get(token=token, used=False)
        user = token_obj.recipient
        
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                token_obj.used = True
                token_obj.save()
                messages.success(request, 'Password reset successfully. You can now login with your new password.')
                return redirect('login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'password_reset_confirm.html', {'form': form, 'token': token})
    except Token.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')

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

"""Information 4: Eligibility Questionnaire"""
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
    subject = "Wave 1 Online Survey Set - Ready"
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
    
"""Information 6: (Website) IRB Consent Form
Participants should be able to access the IRB consent form on the website."""
@login_required
def consent_form(request):
    if request.method == "POST":
        logger.debug(f"Consent form POST data for {request.user.username}: {dict(request.POST)}")
        
        # Check if user declined consent
        consent_choice = request.POST.get('consent')
        if consent_choice == 'no':
            logger.info(f"User {request.user.username} declined consent")
            return redirect('exit_screen_not_interested')
        
        form = ConsentForm(request.POST)
        if form.is_valid():
            user = request.user
            try:
                user_progress = UserSurveyProgress.objects.get(user=user, survey__title="Eligibility Criteria")
                if not user_progress.eligible:
                    logger.warning(f"User {user.username} not eligible")
                    messages.error(request, "You are not eligible to participate.")
                    return redirect("exit_screen_not_eligible")
            except UserSurveyProgress.DoesNotExist:
                logger.error(f"No UserSurveyProgress found for {user.username}")
                messages.error(request, "No eligibility record found. Please contact support.")
                return render(request, "consent_form.html", {"form": form})

            participant, created = Participant.objects.get_or_create(user=user)
            if created:
                logger.info(f"Created Participant for {user.username}")

            # Set timeline for time compression testing
            current_time = timezone.now()
            user_progress.day_1 = current_time.date()  # Reset to today's date
            user_progress.timeline_reference_timestamp = current_time  # Set reference timestamp for time compression
            user_progress.consent_given = True
            user_progress.save()

            # Remove duplicate email sending - let the timeline system handle it
            # if not participant.wave1_survey_email_sent:
            #     participant.send_email("wave1_survey_ready", extra_context={"username": user.username})
            #     participant.wave1_survey_email_sent = True
            #     participant.save()

            # end Jun 25
            try:
                user_progress.save()
                logger.debug(f"Saved progress for {user.username}: consent_given=True, day_1={user_progress.day_1}")
            except Exception as e:
                logger.error(f"Failed to save progress for {user.username}: {e}")
                messages.error(request, "Failed to save consent data. Please try again.")
                return render(request, "consent_form.html", {"form": form})

            # Trigger timeline automation
            try:
                schedule_wave1_monitoring_email(participant.pk)
                logger.info(f"Triggered timeline email scheduling for participant {participant.participant_id}")
            except Exception as e:
                logger.error(f"Failed to trigger timeline email scheduling for {participant.participant_id}: {e}")
                messages.warning(request, "Consent saved, but email scheduling failed. Contact support.")

            logger.info(f"Consent processed successfully for {user.username}")
            return redirect("dashboard")
        else:
            logger.warning(f"Consent form invalid for {request.user.username}: {form.errors}")
            messages.error(request, "Please correct the errors below.")
            return render(request, "consent_form.html", {"form": form})
    else:
        form = ConsentForm()
        return render(request, "consent_form.html", {'form': form})

# INFORMATION 10: Exit Screen for Not Eligible
def exit_screen_not_eligible(request):
    try:
        content = Content.objects.get(content_type='exit_screen')
        return render(request, 'exit_screen_not_eligible.html', {'content': content})
    except Content.DoesNotExist:
        return render(request, 'exit_screen_not_eligible.html')



@login_required
def survey_view(request, wave):
    """Handle survey views for different waves"""
    participant = get_object_or_404(Participant, user=request.user)
    
    # Check if participant is eligible for this survey
    if not participant.user.is_authenticated:
        return redirect('login')
    
    context = {
        'wave': wave,
        'participant': participant,
        'survey_title': f'Wave {wave} Survey',
    }
    
    if wave == 1:
        context['survey_description'] = 'Wave 1 Online Survey Set - Complete this survey within 10 days to earn a $5 Amazon gift card.'
    elif wave == 2:
        context['survey_description'] = 'Wave 2 Online Survey Set - Complete this survey within 10 days to earn a $5 Amazon gift card.'
    elif wave == 3:
        context['survey_description'] = 'Wave 3 Online Survey Set - Complete this survey within 10 days to earn a $5 Amazon gift card.'
    else:
        context['survey_description'] = f'Wave {wave} Survey'
    
    return render(request, 'survey.html', context)

@login_required
def daily_log_view(request, wave):
    """Handle daily activity log views for different waves"""
    participant = get_object_or_404(Participant, user=request.user)
    
    context = {
        'wave': wave,
        'participant': participant,
        'log_title': f'Wave {wave} Daily Activity Log',
    }
    
    if wave == 1:
        context['log_description'] = 'Wave 1 Daily Activity Log - Record your physical activity for the past 7 days.'
    elif wave == 3:
        context['log_description'] = 'Wave 3 Daily Activity Log - Record your physical activity for the past 7 days.'
    else:
        context['log_description'] = f'Wave {wave} Daily Activity Log'
    
    return render(request, 'daily_log.html', context)

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
    # Add debugging information
    print(f"[DEBUG] Dashboard accessed by user: {request.user.username}")
    print(f"[DEBUG] User ID: {request.user.id}")
    print(f"[DEBUG] User is authenticated: {request.user.is_authenticated}")
    
    user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
    participant = Participant.objects.filter(user=request.user).first()
    progress_percentage = 0  # Default if not eligible or study_day not set
    # Add more debugging
    if participant:
        print(f"[DEBUG] Participant found: {participant.participant_id}")
        print(f"[DEBUG] Participant user: {participant.user.username}")
    else:
        print(f"[DEBUG] No participant found for user {request.user.username}")
    
    # Add enrollment status debugging
    if user_progress:
        print(f"[DEBUG] User progress found:")
        print(f"[DEBUG] - Eligible: {user_progress.eligible}")
        print(f"[DEBUG] - Consent given: {user_progress.consent_given}")
        print(f"[DEBUG] - Day 1: {user_progress.day_1}")
    else:
        print(f"[DEBUG] No user progress found for user {request.user.username}")
    
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
    
    # Use compressed timeline calculation consistently
    if user_progress and user_progress.eligible and user_progress.consent_given and participant:
        if not participant.enrollment_date:
            participant.enrollment_date = user_progress.day_1 or current_date
            participant.save()
        if user_progress.day_1 is not None:
            # Use compressed timeline calculation
            study_day = get_study_day(
                user_progress.day_1,
                now=get_current_time(),
                compressed=settings.TIME_COMPRESSION,
                seconds_per_day=settings.SECONDS_PER_DAY,
                reference_timestamp=user_progress.timeline_reference_timestamp
            )
            
            # Calculate compressed timeline milestones
            # In compressed mode, these are study days, not calendar dates
            if settings.TIME_COMPRESSION:
                # For compressed timeline, we work with study days directly
                day_11_study_day = 11
                day_21_study_day = 21
                day_95_study_day = 95
                day_104_study_day = 104
                
                # Calculate days until milestones based on study day difference
                days_until_start_wave1 = max(0, day_11_study_day - study_day)
                days_until_end_wave1 = max(0, day_21_study_day - study_day)
                days_until_start_wave3 = max(0, day_95_study_day - study_day)
                days_until_end_wave3 = max(0, day_104_study_day - study_day)
                
                # For display purposes, convert to approximate real time
                seconds_until_start_wave1 = days_until_start_wave1 * settings.SECONDS_PER_DAY
                seconds_until_end_wave1 = days_until_end_wave1 * settings.SECONDS_PER_DAY
                
                print(f"[DEBUG] Study Day: {study_day}")
                print(f"[DEBUG] Days until start wave 1: {days_until_start_wave1} (study days)")
                print(f"[DEBUG] Days until end wave 1: {days_until_end_wave1} (study days)")
                print(f"[DEBUG] Seconds until start wave 1: {seconds_until_start_wave1}")
                print(f"[DEBUG] Seconds until end wave 1: {seconds_until_end_wave1}")
            else:
                # For real timeline, use calendar dates
                day_11 = user_progress.day_1 + timedelta(days=10)
                day_21 = user_progress.day_1 + timedelta(days=20)
                day_95 = user_progress.day_1 + timedelta(days=94)
                day_104 = user_progress.day_1 + timedelta(days=103)
                
                days_until_start_wave1 = max(0, (day_11 - current_date).days)
                days_until_end_wave1 = max(0, (day_21 - current_date).days)
                days_until_start_wave3 = max(0, (day_95 - current_date).days)
                days_until_end_wave3 = max(0, (day_104 - current_date).days)
                
            print(f"[DEBUG] Day 11: {day_11}")
            print(f"[DEBUG] Day 21: {day_21}")
            print(f"[DEBUG] Day 95: {day_95}")
            print(f"[DEBUG] Day 104: {day_104}")
            print(f"[DEBUG] Days until start wave 1: {days_until_start_wave1}")
            print(f"[DEBUG] Days until end wave 1: {days_until_end_wave1}")

            # ----  Study progress percentage ----
            total_study_days = 113  # Set this to your full study duration
            progress_percentage = min(int((study_day / total_study_days) * 100), 100)
            print(f"[DEBUG] Progress percentage: {progress_percentage}")

            within_wave1_period = study_day is not None and 11 <= study_day <= 20 and not participant.code_entered
            print(f"[DEBUG] Within wave 1 period: {within_wave1_period}")
            within_wave3_period = study_day is not None and 95 <= study_day <= 104 and not participant.wave3_code_entered
            print(f"[DEBUG] Within wave 3 period: {within_wave3_period}")
            
            # Set display dates for template
            if settings.TIME_COMPRESSION:
                start_date_wave1 = f"Study Day {day_11_study_day}"
                end_date_wave1 = f"Study Day {day_21_study_day}"
                start_date_wave3 = f"Study Day {day_95_study_day}"
                end_date_wave3 = f"Study Day {day_104_study_day}"
            else:
                start_date_wave1 = day_11
                end_date_wave1 = day_21
                start_date_wave3 = day_95
                end_date_wave3 = day_104

    context = {
        'user': request.user,  # Explicitly pass the current user
        'progress': user_progress,
        'participant': participant,
        'within_wave1_period': within_wave1_period,
        'within_wave3_period': within_wave3_period,
        'days_until_start_wave1': days_until_start_wave1,
        'days_until_end_wave1': days_until_end_wave1,
        'start_date_wave1': start_date_wave1,
        'end_date_wave1': end_date_wave1,
        'days_until_start_wave3': days_until_start_wave3 if 'days_until_start_wave3' in locals() else 0,
        'days_until_end_wave3': days_until_end_wave3 if 'days_until_end_wave3' in locals() else 0,
        'start_date_wave3': start_date_wave3 if 'start_date_wave3' in locals() else None,
        'end_date_wave3': end_date_wave3 if 'end_date_wave3' in locals() else None,
        'study_day': study_day if user_progress else 0,  # For debugging
        'needs_consent': user_progress and user_progress.eligible and not user_progress.consent_given,  # New flag
        'progress_percentage': progress_percentage,
        'time_compression': settings.TIME_COMPRESSION,  # Add this for template debugging
        'intervention_points': participant.intervention_points if participant else 0,  # Add intervention points
    }
    return render(request, "dashboard.html", context)
# INFORMATION 11 & 22: Enter Code
@login_required
def enter_code(request, wave):
    """Handle code entry for Wave 1 or Wave 3"""
    participant = get_object_or_404(Participant, user=request.user)
    user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
    if not user_progress or not user_progress.day_1:
        messages.error(request, "Enrollment date not set. Contact support.")
        return redirect('home')

    # Use compressed timeline calculation consistently
    now = get_current_time()
    if user_progress and user_progress.day_1:
        study_day = get_study_day(
            user_progress.day_1,
            now=now,
            compressed=settings.TIME_COMPRESSION,
            seconds_per_day=settings.SECONDS_PER_DAY,
            reference_timestamp=user_progress.timeline_reference_timestamp
        )
    else:
        study_day = 1  # Default to day 1 if no day_1 set
    
    # Add debugging
    print(f"[DEBUG] Enter code - Wave: {wave}")
    print(f"[DEBUG] Study day: {study_day}")
    print(f"[DEBUG] Day 1: {user_progress.day_1}")
    print(f"[DEBUG] Current time: {now}")
    print(f"[DEBUG] Time compression: {settings.TIME_COMPRESSION}")
    print(f"[DEBUG] Seconds per day: {settings.SECONDS_PER_DAY}")
    
    if wave == 1:
        # Check if within Wave 1 window (Days 11-20)
        print(f"[DEBUG] Wave 1 check: 11 <= {study_day} <= 20 = {11 <= study_day <= 20}")
        if not (11 <= study_day <= 20):
            messages.error(request, f"Code entry is not available at this time. Current study day: {study_day}, required: 11-20")
            return redirect('home')
        if participant.code_entered:
            messages.info(request, "You have already entered the code for Wave 1.")
            return redirect('home')
            
    elif wave == 3:
        # Check if within Wave 3 window (Days 95-104)
        print(f"[DEBUG] Wave 3 check: 95 <= {study_day} <= 104 = {95 <= study_day <= 104}")
        if not (95 <= study_day <= 104):
            messages.error(request, f"Code entry is not available at this time. Current study day: {study_day}, required: 95-104")
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
                    # Jun 25: Add in store timeline day instead of date 
                    participant.code_entered = True
                    # Use compressed timeline calculation for code_entry_day
                    if user_progress and user_progress.day_1:
                        participant.code_entry_day = get_study_day(
                            user_progress.day_1,
                            now=now,
                            compressed=settings.TIME_COMPRESSION,
                            seconds_per_day=settings.SECONDS_PER_DAY,
                            reference_timestamp=user_progress.timeline_reference_timestamp
                        )
                    else:
                        participant.code_entry_day = 1
                    
                    # Set code entry date for email task
                    participant.code_entry_date = timezone.now().date()
                    participant.save()
                    
                    # Send Information 12 email - use participant.id (database ID)
                    send_wave1_code_entry_email(participant.id)
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
                    # Set Wave 3 code entry day using compressed timeline
                    if user_progress and user_progress.day_1:
                        participant.wave3_code_entry_day = get_study_day(
                            user_progress.day_1,
                            now=now,
                            compressed=settings.TIME_COMPRESSION,
                            seconds_per_day=settings.SECONDS_PER_DAY,
                            reference_timestamp=user_progress.timeline_reference_timestamp
                        )
                    else:
                        participant.wave3_code_entry_day = 1
                    participant.save()
                    
                    # Send Information 23 email - use participant.id (database ID)
                    send_wave3_code_entry_email(participant.id)
                    messages.success(request, "Code entered successfully!")
                    return redirect('code_success', wave=wave)
                
                messages.success(request, "Code entered successfully!")
                return redirect('code_success', wave=wave)
            else:
                return render(request, "dashboard.html", { "form": form,  "code_error": "Incorrect code. Please try again.",
   # Include other context vars needed on the dashboard
})
                # messages.error(request, "Incorrect code. Please try again.")
    else:
        form = CodeEntryForm()
    
    context = {
        'form': form,
        'wave': wave,
        'days_remaining': 20 - study_day if wave == 1 else 104 - study_day,
    }
    return render(request, 'monitoring/enter_code.html', context)

def download_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pas_data.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Participant ID', 'Username', 'Email', 'Phone Number', 'Registration Code',
        'Confirmation Date', 'Interest Submitted', 'Interested', 'Eligibility Submitted',
        'Is Eligible', 'Consent Submitted', 'Consented', 'Wave 1 Code Entered',
        'Wave 1 Code Date', 'Group', 'Wave 3 Code Entered', 'Wave 3 Code Date'
    ])
    participants = Participant.objects.all()
    for p in participants:
        survey_progress = SurveyProgress.objects.filter(user=p.user).first()
        writer.writerow([
            p.participant_id, p.user.username, p.email, p.phone_number, 'wavepa',
            p.is_confirmed and p.token_expiration or '', survey_progress and survey_progress.interest_submitted or False,
            survey_progress and survey_progress.interested or False, survey_progress and survey_progress.eligibility_submitted or False,
            survey_progress and survey_progress.is_eligible or False, survey_progress and survey_progress.consent_submitted or False,
            survey_progress and survey_progress.consented or False, p.code_entered, p.code_entry_date,
            p.group, p.wave3_code_entered, p.wave3_code_entry_date
        ])
    return response

def code_success(request, wave):
    # return render(request, 'code_success.html', {'wave': wave})
    participant = Participant.objects.get(user=request.user)
    current_date = timezone.now().date()
    day_21 = participant.enrollment_date + timedelta(days=20)
    days_remaining = (day_21 - current_date).days
    return render(request, 'code_success.html', {'days_remaining': days_remaining})

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
    try:
        content = Content.objects.get(content_type='waiting_screen')
        return render(request, "waiting_screen.html", {'content': content})
    except Content.DoesNotExist:
        return render(request, "waiting_screen.html")

def logout_view(request):
    print(f"[DEBUG] Logging out user: {request.user.username}")
    logout(request)
    # Clear all session data
    request.session.flush()
    print(f"[DEBUG] Session cleared, redirecting to landing")
    return redirect('landing')  # Redirect to the landing page after logout

@login_required
def intervention_access(request):
    """Handle intervention access for participants"""
    try:
        participant = Participant.objects.get(user=request.user)
        user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
        
        if not user_progress or not user_progress.consent_given:
            messages.error(request, "You must complete enrollment before accessing the intervention.")
            return redirect('dashboard')
        
        # Calculate study day using compressed timeline
        study_day = get_study_day(
            user_progress.day_1,
            now=get_current_time(),
            compressed=settings.TIME_COMPRESSION,
            seconds_per_day=settings.SECONDS_PER_DAY
        )
        
        # Check if participant should have access
        has_access = False
        access_message = ""
        
        if participant.randomized_group == 1:  # Intervention group
            if 29 <= study_day <= 56:
                has_access = True
                access_message = "You have access to the intervention from Day 29 to Day 56."
                if not participant.intervention_access_granted:
                    participant.intervention_access_granted = True
                    participant.intervention_access_date = get_current_time()
                    participant.save()
            else:
                access_message = "Your intervention access period has ended (Days 29-56)."
        elif participant.randomized_group == 0:  # Control group
            if study_day > 112:
                has_access = True
                access_message = "You now have access to the intervention after study completion."
                if not participant.intervention_access_granted:
                    participant.intervention_access_granted = True
                    participant.intervention_access_date = get_current_time()
                    participant.save()
            else:
                access_message = "You will receive intervention access after Day 113 (study completion)."
        else:
            access_message = "You have not been assigned to a group yet."
        
        context = {
            'participant': participant,
            'study_day': study_day,
            'has_access': has_access,
            'access_message': access_message,
            'challenges_completed': participant.challenges_completed,
            'intervention_login_count': participant.intervention_login_count,
            'progress_percent': min(int((participant.challenges_completed / 24) * 100), 100) if participant.challenges_completed is not None else 0,
            'remaining_challenges': max(0, 24 - (participant.challenges_completed or 0)),
        }
        
        return render(request, 'intervention_access.html', context)
        
    except Participant.DoesNotExist:
        messages.error(request, "Participant record not found.")
        return redirect('dashboard')

@login_required
def intervention_challenge_25(request):
    """Render Challenge 25: Leisure-Related Physical Activity demo."""
    participant = get_object_or_404(Participant, user=request.user)
    context = {
        'participant': participant,
        'current_points': participant.intervention_points,
    }
    return render(request, 'interventions/challenge_25.html', context)

@login_required
def intervention_challenge_1(request):
    """Render Challenge 1: Introduction."""
    participant = get_object_or_404(Participant, user=request.user)
    context = {
        'participant': participant,
    }
    return render(request, 'interventions/challenge_1.html', context)

@login_required
def intervention_challenge_2(request):
    """Render Introductory Challenge 2: Contents."""
    participant = get_object_or_404(Participant, user=request.user)
    context = {
        'participant': participant,
    }
    return render(request, 'interventions/challenge_2.html', context)

@login_required
def intervention_challenge_4(request):
    """Render Introductory Challenge 4: Review."""
    participant = get_object_or_404(Participant, user=request.user)
    context = {
        'participant': participant,
    }
    return render(request, 'interventions/challenge_4.html', context)

@login_required
def intervention_challenge_5(request):
    """Render and handle Introductory Challenge 5: Self-efficacy."""
    participant = get_object_or_404(Participant, user=request.user)
    if request.method == 'POST':
        try:
            q1 = int(request.POST.get('q1'))
            q2 = int(request.POST.get('q2'))
            q3 = int(request.POST.get('q3'))
            q4 = int(request.POST.get('q4'))
            q5 = int(request.POST.get('q5'))
            q6 = int(request.POST.get('q6'))
            q7 = int(request.POST.get('q7'))
        except (TypeError, ValueError):
            messages.error(request, 'Please answer all questions before submitting.')
            return redirect('intervention_challenge_5')

        from .models import Challenge5Response
        Challenge5Response.objects.create(
            user=request.user,
            participant=participant,
            q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7
        )
        messages.success(request, 'Responses saved. Thank you!')
        return redirect('intervention_access')

    context = { 'participant': participant }
    return render(request, 'interventions/challenge_5.html', context)

@staff_member_required
def export_challenge_5_csv(request):
    """Export Challenge 5 responses as CSV (staff only)."""
    from .models import Challenge5Response
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="challenge5_responses.csv"'
    writer = csv.writer(response)
    writer.writerow(['username', 'participant_id', 'created_at', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'])
    for r in Challenge5Response.objects.select_related('user', 'participant').all():
        writer.writerow([
            r.user.username,
            r.participant.participant_id,
            r.created_at.isoformat(),
            r.q1, r.q2, r.q3, r.q4, r.q5, r.q6, r.q7
        ])
    return response

@login_required
def ge_challenge_1(request):
    """General Education - Challenge 1: Physical Activity"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_1.html', context)

@login_required
def ge_challenge_2(request):
    """General Education - Challenge 2: Importance"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_2.html', context)

@login_required
def ge_challenge_3(request):
    """General Education - Challenge 3: How to do (Part 1)"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_3.html', context)

@login_required
def ge_challenge_4(request):
    """General Education - Challenge 4: How to do (Part 2)"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_4.html', context)

@login_required
def ge_challenge_5(request):
    """General Education - Challenge 5: How to do (Part 3)"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_5.html', context)

@login_required
def ge_challenge_6(request):
    """General Education - Challenge 6: Review"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/ge_challenge_6.html', context)

@login_required
def wr_challenge_7(request):
    """Work-Related Physical Activity - Challenge 7: Learning"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/wr_challenge_7.html', context)

@login_required
def wr_challenge_8(request):
    """Work-Related Physical Activity - Challenge 8: Easy Task"""
    participant = get_object_or_404(Participant, user=request.user)
    
    if request.method == 'POST':
        from .models import WorkRelatedChallenge8Response
        
        # Save responses
        WorkRelatedChallenge8Response.objects.create(
            user=request.user,
            participant=participant,
            answer1=request.POST.get('answer1', ''),
            answer2=request.POST.get('answer2', ''),
            answer3=request.POST.get('answer3', ''),
            answer4=request.POST.get('answer4', ''),
        )
        messages.success(request, "Your responses have been recorded. Thank you!")
        return redirect('intervention_access')
    
    context = { 'participant': participant }
    return render(request, 'interventions/wr_challenge_8.html', context)

@login_required
def wr_challenge_9(request):
    """Work-Related Physical Activity - Challenge 9: Story"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 'participant': participant }
    return render(request, 'interventions/wr_challenge_9.html', context)

@login_required
def wr_challenge_10(request):
    """Work-Related Physical Activity - Challenge 10: Office Fitness Game"""
    participant = get_object_or_404(Participant, user=request.user)
    context = { 
        'participant': participant,
        'current_points': participant.intervention_points if participant else 0
    }
    return render(request, 'interventions/wr_challenge_10.html', context)

@login_required
def update_intervention_points(request):
    """Handle AJAX requests to update intervention points."""
    if request.method == 'POST':
        try:
            participant = Participant.objects.get(user=request.user)
            points_to_add = int(request.POST.get('points', 0))
            
            # Update points
            participant.intervention_points += points_to_add
            participant.save()
            
            return JsonResponse({
                'success': True,
                'new_total': participant.intervention_points,
                'points_added': points_to_add
            })
        except (Participant.DoesNotExist, ValueError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def intervention_access_test(request):
    """Test version of intervention access that bypasses study day restrictions."""
    try:
        participant = Participant.objects.get(user=request.user)
        user_progress = UserSurveyProgress.objects.filter(user=request.user, survey__title="Eligibility Criteria").first()
        
        if not user_progress or not user_progress.consent_given:
            messages.error(request, "You must complete enrollment before accessing the intervention.")
            return redirect('dashboard')
        
        has_access = True
        access_message = "TEST MODE: Intervention access granted for testing purposes."
        
        context = {
            'participant': participant,
            'study_day': 50,  # Fake study day for testing
            'has_access': has_access,
            'access_message': access_message,
            'challenges_completed': participant.challenges_completed,
            'intervention_login_count': participant.intervention_login_count,
            'progress_percent': min(int((participant.challenges_completed / 24) * 100), 100) if participant.challenges_completed is not None else 0,
            'remaining_challenges': max(0, 24 - (participant.challenges_completed or 0)),
        }
        
        return render(request, 'intervention_access.html', context)
        
    except Participant.DoesNotExist:
        messages.error(request, "Participant record not found.")
        return redirect('dashboard')
