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
from .forms import CodeEntryForm
# from .tasks.tasks import send_scheduled_email

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from testpas.models import User, Token, UserSurveyProgress

# 1️⃣ User Registration
def create_account(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        user = User.objects.create_user(username=username, email=email, password=password)
        token = Token.objects.create(recipient=user)  # Generate a confirmation token
        
        # Send confirmation email
        confirmation_url = f"{request.build_absolute_uri('/confirm-account/')}?token={token.token}"
        send_mail(
            "Confirm Your Account",
            f"Click the link to confirm your account: {confirmation_url}",
            "vuleson59@gmail.com",
            [user.email], [token.token]
        )

        return JsonResponse({"message": "Account created. Check your email to confirm."})
    
    return render(request, "create_account.html")

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

def create_participant(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number").strip()

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        # Create user account
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create participant profile
        participant = Participant.objects.create(
            user=user, email=email, phone_number=phone_number, confirmation_token=str(uuid.uuid4())
        )

        return JsonResponse({"message": "Participant registered successfully!"})

    return render(request, "create_participant.html")


# 3️⃣ Questionnaire for Eligibility
@login_required
def questionnaire(request):
    if request.method == "POST":
        user = request.user
        answers = request.POST  # Process answers from form submission
        # Debug: Print the raw POST data to check if values are missing
        print(f"Full POST Data: {answers}")

        # Eligibility check logic
        age = int(answers.get("age", 0))
        height = int(answers.get("height", 0))  # Inches
        weight = int(answers.get("weight", 0))  # Pounds
        access_to_device = answers.get("has_device", "").strip().lower() == "yes"
        willing_no_other_study = answers.get("not_enroll_other", "").strip().lower() == "yes"
        willing_monitor = answers.get("comply_monitoring", "").strip().lower() == "yes"
        willing_contact = answers.get("respond_contacts", "").strip().lower() == "yes"
        # BMI Calculation
        bmi = (weight / (height ** 2)) * 703  # Convert inches/lbs to BMI
        print(f"Debugging Eligibility Check:")
        print(f"Age: {age}, Height: {height}, Weight: {weight}, BMI: {bmi:.2f}")
        print(f"Device Access: {access_to_device}, No Other Study: {willing_no_other_study}")
        print(f"Willing to Monitor: {willing_monitor}, Willing to Contact: {willing_contact}")

        existing_progress = UserSurveyProgress.objects.filter(user=user).first()

        # Eligibility Conditions
        eligible = (
            (18 <= age <= 64) and  # Age requirement
            (bmi >= 25) and        # BMI requirement
            access_to_device and    # Must have device access
            willing_no_other_study and  # Must not enroll in another study
            willing_monitor and  # Must agree to monitoring
            willing_contact  # Must agree to respond to research contact
        )
        print(f"Eligibility Result: {eligible}")  # Debug final eligibility result
        survey = Survey.objects.first()
        if existing_progress:
            existing_progress.eligible = eligible  # ✅ Updates existing record
            existing_progress.save()
        else:
            UserSurveyProgress.objects.create(user=user, survey=survey, eligible=eligible, consent_given=False)


        
        if not survey:
            return JsonResponse({"error": "No survey available. Contact support."}, status=500)

        existing_progress = UserSurveyProgress.objects.filter(user=user).first()

        if existing_progress:
            existing_progress.eligible = eligible
            existing_progress.save()
        else:
            UserSurveyProgress.objects.create(user=user, survey=survey, eligible=eligible, consent_given=False)

        if eligible:
            return redirect("consent_form")
        else:
            # return redirect(("exit_screen_not_eligible"))
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
def exit_screen_not_interested(request):
    if request.method == 'GET':
        return render(request, 'exit_screen_not_interested.html')


def exit_screen_not_eligible(request):
    return render(request, 'exit_screen_not_eligible.html')

# 4️⃣ Consent Form
@login_required
def consent_form(request):
    if request.method == "POST":
        user = request.user
        user_progress = UserSurveyProgress.objects.filter(user=user).last()
        # user_progress.consent_given = True
        # user_progress.day_1 = timezone.now().date()  # Set Day 1 as today
        # user_progress.save()
        if user_progress and user_progress.eligible:
            user_progress.consent_given = True
            user_progress.day_1 = timezone.now().date()
            user_progress.save()
        send_wave_1_email(request.user)

        return redirect("/waiting-screen/")

    return render(request, "consent_form.html")

# 5️⃣ Waiting Screen
@login_required
def waiting_screen(request):
    return render(request, "waiting_screen.html")

# 6️⃣ Dashboard
@login_required
def dashboard(request):
    user_progress = UserSurveyProgress.objects.filter(user=request.user).first()
    return render(request, "dashboard.html", {"progress": user_progress})

@login_required
def enter_code(request):
    participant = Participant.objects.get(user=request.user)
    current_date = timezone.now().date()

    day_11 = participant.enrollment_date + timedelta(days=0)
    day_21 = participant.enrollment_date + timedelta(days=1)

    if current_date < day_11:
        messages.error(request, "You cannot enter the code before Day 11.")
        return redirect('home')

    if current_date > day_21:
        messages.error(request, "The time window for entering the code has passed.")
        return redirect('home')

    if request.method == 'POST':
        form = CodeEntryForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].strip().lower()
            if code == 'wavepa':
                participant.code_entered = True
                participant.code_entry_date = current_date
                participant.save()
                participant.send_code_entry_email()
                messages.success(request, "Code entered successfully!")
                return redirect('code_success')
            else:
                messages.error(request, "Incorrect code. Please try again.")
    else:
        form = CodeEntryForm()

    return render(request, 'enter_code.html', {
        'form': form,
        'days_remaining': (day_21 - current_date).days
    })


# 7️⃣ Challenge System (Enter Code)
@login_required
def enter_wave_1_code(request):
    user_progress = UserSurveyProgress.objects.filter(user=request.user).first()

    if not user_progress:
        return JsonResponse({"error": "User progress not found."}, status=400)

    today = timezone.now().date()
    day_1 = user_progress.day_1
    day_11 = day_1 + timedelta(days=10)
    day_20 = day_1 + timedelta(days=20)
    day_21 = day_1 + timedelta(days=21)

    # Only allow code entry from Day 11 to Day 20
    if not (day_11 <= today <= day_20):
        return JsonResponse({"error": "Code entry is not available at this time."}, status=400)

    if request.method == "POST":
        entered_code = request.POST.get("code", "").strip().lower()
        correct_code = "wavepa"

        if entered_code == correct_code:
            Challenge.objects.create(user=request.user, description="Wave 1 Code Entered", completed=True)

            # Send immediate email (Information 12)
            send_mail(
                "Physical Activity Monitoring Tomorrow (Wave 1)",
                f"Hi {request.user.username},\n\nYou have successfully entered the access code. Please start wearing the monitor tomorrow!",
                "vuleson59@gmail.com",
                [request.user.email]
            )

            return JsonResponse({"message": "Code accepted. Please check your email for further instructions."})
        else:
            return JsonResponse({"error": "Incorrect code. Please try again."}, status=400)

    return render(request, "enter_wave_1_code.html")

@login_required
def code_success(request):
    return render(request, 'code_success.html')
@login_required
def code_failure(request):
    return render(request, 'code_failure.html')

# 8️⃣ Send Missed Code Entry Email (Day 21)
def check_missed_code_entry():
    today = timezone.now().date()
    participants = Participant.objects.filter(code_entered=False, enrollment_date__lte=today - timedelta(days=20))

    for participant in participants:
        send_mail(
            "Missing Code Entry (Wave 1)",
            f"Hi {participant.user.username},\n\nYou missed the code entry (i.e., no $35 worth of Amazon electronic gift cards). However, you will still have more tasks in the future. We will contact you via email, so please regularly check your inbox.",
            "vuleson59@gmail.com",
            [participant.user.email]
        )

def check_day_21(request):
    participants = Participant.objects.filter(
        enrollment_date=timezone.now().date() - timedelta(days=20),
        code_entered=False,
        email_sent=False
    )
    for participant in participants:
        participant.send_missing_code_email()
    # return redirect('/admin/')  # Redirect to admin page after checking

    # current_time = get_current_time()
    user = request.user
    if not user.is_authenticated:
        return redirect('login')  # Redirect to login page if user is not authenticated

    participant = Participant.objects.get(user=request.user)
    start_date = participant.enrollment_date
    # current_date = timezone.now().date()

    # Use a test date if provided, otherwise use the current date
    test_date_str = request.GET.get('test_date')
    if test_date_str:
        current_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()
    day_11 = start_date + timedelta(days=10)
    day_21 = start_date + timedelta(days=20)
    # day_11 = participant.enrollment_date + timedelta(days=10)  
    # day_21 = participant.enrollment_date + timedelta(days=20)  

    # For testing purposes, freeze the date to within the code entry window
    with freeze_time(day_11 + timedelta(days=1)):  # Simulate Day 12
        current_date = timezone.now().date()

    # Check if we're in the valid date range
    if current_date < day_11 or current_date > day_21:
        messages.error(request, "You can only enter the code between Day 11 and Day 20.")
        return redirect('home') # Redirect to home page if not in the valid date range
        
    if request.method == 'POST':
        form = CodeEntryForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].strip().lower()
            if code == 'wavepa':
                participant.code_entered = True
                participant.code_entry_date = current_date
                participant.save()

                # Email content
                subject = "Physical Activity Monitoring Tomorrow (Wave 1)"
                message = f"""
                Hi {request.user.username},

                You have successfully entered the access code for physical activity monitoring. Thank you!

                Please start wearing the monitor tomorrow for seven consecutive days. For example, 
                
                if you enter the code on {current_date.strftime('%m/%d/%Y')} (Fri), 
                please wear the device starting on {(current_date + timedelta(days=1)).strftime('%m/%d/%Y')} (Sat) 
                and continue wearing it until {(current_date + timedelta(days=7)).strftime('%m/%d/%Y')} (Fri).

                To earn $35 in Amazon gift cards, please wear the monitor for at least 4 days, 
                including one weekend day, with at least 10 hours each day. For the following seven days, 
                complete the daily log at the end of each day. You will receive your total incentives after the study ends.

                If you need any assistance or have any questions at any time, 
                please contact Seungmin (“Seung”) Lee (Principal Investigator) at seunglee@iastate.edu or 517-898-0020.

                Sincerely,

                The Obesity and Physical Activity Research Team
                """

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email, settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False
                )

                messages.success(request, "Code entered successfully!")
                return redirect('code_success')
            else:
                return render(request, 'enter_code.html', {
                    'form': form,
                    'error': 'Incorrect code. Please try again.'
                })
    else:
        form = CodeEntryForm()

    return render(request, 'enter_code.html', {
        'form': form,
        'days_remaining': (day_21 - current_date).days
    })
# 8️⃣ Automatically Send Missed Code Entry Email (Day 21)
def check_missed_challenges():
    today = timezone.now().date()
    user_progresses = UserSurveyProgress.objects.filter(day_1__isnull=False)

    for progress in user_progresses:
        day_21 = progress.day_1 + timedelta(days=21)

        if today == day_21:
            challenge = Challenge.objects.filter(user=progress.user, description="Wave 1 Code Entered").first()

            if not challenge:  # User never entered the code
                send_mail(
                    "Missed Wave 1 Code Entry",
                    f"Hi {progress.user.username},\n\nYou did not enter the Wave 1 code in time. Please contact the research team for further assistance.",
                    "vuleson59@gmail.com",
                    [progress.user.email]
                )

@csrf_exempt
def send_scheduled_email(request):
    if request.method == 'POST':
        # Extract email details from the request (e.g., JSON data)
        subject = request.POST.get('subject', 'Default Subject')
        message = request.POST.get('message', 'Default Message')
        from_email = request.POST.get('from_email', DEFAULT_FROM_EMAIL)
        # recipient_list = request.POST.getlist('recipient_list', ['vuleson59@gmail.com'])
        recipient_list = request.POST.get('recipient_list', '').split(',')

        # Trigger the Celery task to send an email asynchronously
        send_scheduled_email.delay(subject, message, from_email, recipient_list)
       
        # Return a JSON response indicating success
        return JsonResponse({'status': 'Email scheduled successfully'})

    # Return a JSON response indicating invalid request method
    return render(request, 'send_scheduled_email.html')
# 9️⃣ Home Page
@login_required
def home(request):
    participant, created = Participant.objects.get_or_create(
        user=request.user,
        defaults={
            'enrollment_date': timezone.now().date(),
            'code_entered': False
        }
    )
    current_date = timezone.now().date()
    
    day_11 = participant.enrollment_date + timedelta(days=10)
    day_21 = participant.enrollment_date + timedelta(days=20)
    
    within_wave1_period = day_11 <= current_date <= day_21

    context = {
        'user': request.user,
        'progress': participant,
        'within_wave1_period': within_wave1_period,
        'days_until_start': (day_11 - current_date).days if current_date < day_11 else 0,
        'days_until_end': (day_21 - current_date).days if current_date <= day_21 else 0,
        'start_date': day_11,
        'end_date': day_21
    }
    return render(request, 'home.html', context)

# 9️⃣ Login & Logout
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return JsonResponse({"error": "Invalid login credentials."}, status=400)

    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login/")
