from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
import json
from hashlib import sha256
from testpas.settings import DEFAULT_FROM_EMAIL
from .models import *
from .utils import validate_token
import uuid
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from freezegun import freeze_time
import os
import datetime
from twilio.rest import Client
import pytz
from .models import Participant
from .forms import CodeEntryForm
# from .tasks.tasks import send_scheduled_email
_fake_time = None

def get_current_time():
    global _fake_time
    if _fake_time is not None:
        return _fake_time
    return timezone.now()

def get_current_date(request):
    mock_date = request.GET.get('mock_date')
    if mock_date:
        return timezone.datetime.strptime(mock_date, '%Y-%m-%d').date()
    return timezone.now().date()
# For developers only
def dev_time_controls(request):
    if not settings.DEBUG:
        return redirect('dashboard')
    
    global _fake_time
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'reset':
            _fake_time = None
            messages.success(request, 'Time reset to current time')
        elif action == 'add_days':
            days = int(request.POST.get('days', 1))
            if _fake_time is None:
                _fake_time = timezone.now()
            _fake_time += timedelta(days=days)
            messages.success(request, f'Added {days} days. Current time: {_fake_time}')
        elif action == 'set_date':
            date_str = request.POST.get('date')
            try:
                _fake_time = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
                messages.success(request, f'Time set to: {_fake_time}')
            except ValueError:
                messages.error(request, 'Invalid date format')
    
    return render(request, 'dev_time_controls.html', {
        'current_time': get_current_time(),
        'real_time': timezone.now(),
    })

def send_wave_1_email(user):
    subject = 'Wave 1 Online Survey Set – Ready'
      # Use an absolute path to the email content file
    email_file_path = os.path.join(settings.BASE_DIR, 'testpas', 'wave_1_email.txt')
    
    # Read the email content from the text file
    with open(email_file_path, 'r') as file:
        message = file.read().format(username=user.username)  
    # # Read the email content from a text file
    # with open('wave_1_email.txt', 'r') as file:
    #     message = file.read().format(username=user.username)
    
    # Send email to the participant and CC the research team
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in settings.py
        [user.email, DEFAULT_FROM_EMAIL],
        fail_silently=False,
    )

# Eligibility check function
def eligibility_check(data):
    age = int(data.get('age'))
    if age < 18 or age > 64:
        return False, 'Age requirement not met. Must be between 18 and 64 years.'

    height = int(data.get('height'))  # in inches
    weight = int(data.get('weight'))  # in lbs
    bmi = (weight / (height ** 2)) * 703
    if bmi < 25.0:
        return False, 'BMI must be greater than or equal to 25.'

    has_device = data.get('has_device', '').lower() == 'yes'
    if not has_device:
        return False, 'Must have access to a technological device to participate.'

    not_enroll_other = data.get('not_enroll_other', '').lower() == 'yes'
    if not not_enroll_other:
        return False, 'Must agree not to enroll in another research-based intervention program.'

    comply_monitoring = data.get('comply_monitoring', '').lower() == 'yes'
    if not comply_monitoring:
        return False, 'Must agree to comply with physical activity monitoring requirements.'

    respond_contacts = data.get('respond_contacts', '').lower() == 'yes'
    if not respond_contacts:
        return False, 'Must agree to respond to study-related contacts.'

    return True, 'Eligible'

@csrf_exempt
def create_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            registration_code = data.get('registration-code', '').strip().lower()
            user_id = data.get('user-id').strip()
            password = data.get('password', '')
            password_confirmation = data.get('password-confirmation', '')
            email = data.get('email').strip().lower()
            phone_number = data.get('phone-number', '').strip()

            if registration_code != 'wavepa':
                return JsonResponse({'error': 'Invalid registration code.'}, status=400)

            if password != password_confirmation:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            if User.objects.filter(username=user_id).exists():
                return JsonResponse({'error': 'User ID already taken.'}, status=400)

            user = User.objects.create_user(username=user_id, password=password, email=email)
            user.is_active = False
            user.save()

            token_value = str(uuid.uuid4())
            Token.objects.create(recipient=user, token=token_value)

            confirmation_link = f"{settings.BASE_URL}/confirm-account/?token={token_value}"
            send_mail(
                'Confirm Your Account',
                f'Thank you for registering. Please confirm your account by clicking the link below:\n\n{confirmation_link}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            # send_mail(
            #     'Confirm Your Account',
            #     f'Thank you for registering. Please confirm your account by clicking the link below:\n\n{confirmation_link}',
            #     'noreply@example.com',
            #     [email],
            #     fail_silently=False,
            # )

            return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return render(request, 'create_account.html')
    # if request.method == 'POST':
    #     # Parse JSON with error handling
    #         try:
    #             data = json.loads(request.body)
    #         except json.JSONDecodeError as e:
    #             return JsonResponse({'error': f'Invalid JSON format: {str(e)}'}, status=400)

    #         # Extract and validate required fields
    #         required_fields = {
    #             'registration-code': '',
    #             'user-id': '',
    #             'password': '',
    #             'password-confirmation': '',
    #             'email': '',
    #             'phone-number': '',
    #             'age': '0',
    #             'has_device': 'no',
    #             'not_enroll_other': 'no',
    #             'comply_monitoring': 'no',
    #             'respond_contacts': 'no'
    #         }

    #         # Set default values for missing fields
    #         for field, default in required_fields.items():
    #             if field not in data:
    #                 data[field] = default
    #             elif isinstance(data[field], str):
    #                 data[field] = data[field].strip()

    #         # Perform eligibility check with error handling
    #         try:
    #             is_eligible, eligibility_reason = eligibility_check(data)
    #             if not is_eligible:
    #                 return JsonResponse({"error": eligibility_reason}, status=400)
    #         except (TypeError, ValueError) as e:
    #             return JsonResponse({"error": f"Invalid eligibility data: {str(e)}"}, status=400)

    
    #         registration_code = data.get('registration-code')
    #         if registration_code != 'wavepa':
    #             return JsonResponse({'error': 'Invalid registration code.'}, status=400)

    #         email = data.get('email')
    #         password = data.get('password')
    #         password_confirmation = data.get('password-confirmation')
    #         if password != password_confirmation:
    #             return JsonResponse({'error': 'Passwords do not match.'}, status=400)

    #         user_id = data.get('user-id')
    #         if User.objects.filter(username=user_id).exists():
    #             return JsonResponse({'error': 'User ID already taken.'}, status=400)
            
    #         # Generate and hash a unique token
    #         token = get_random_string(64)
    #         token_hash = sha256(token.encode()).hexdigest()

    #         user = User.objects.create_user(username=user_id, password=password, email=email)
    #         user.is_active = False
            
    #         user.profile.confirmation_token = token_hash
    #         user.profile.token_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)

    #         user.save()

    #         token_value = str(uuid.uuid4())
    #         Token.objects.create(recipient=user, token=token_value)

    #         confirmation_link = f"{settings.BASE_URL}/confirm-account/?token={token_value}"
            
    #         send_mail(
    #             'Confirm Your Account',
    #             f'Thank you for registering. Please confirm your account by clicking the link below:\n\n{confirmation_link}',
    #             settings.DEFAULT_FROM_EMAIL,  # Use the verified "from" email address
    #             [user.email],
    #             fail_silently=False,
    #         )
    #         return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})

    # return render(request, 'create_account.html')

def confirm_account(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        token_hash = sha256(token.encode()).hexdigest()
        user_profile = get_object_or_404(UserProfile, confirmation_token=token_hash, token_expiration__gte=datetime.datetime.now())
        
        # Confirm the user's account
        user_profile.user.is_active = True
        user_profile.confirmation_token = None
        user_profile.token_expiration = None
        user_profile.save()
        
        return JsonResponse({"message": "Your account has been confirmed successfully."})
    return JsonResponse({"error": "Invalid request method"}, status=405)
# def confirm_account(request):
#     token_value = request.GET.get('token')
#     try:
#         token = Token.objects.get(token=token_value, used=False)
#         user = token.recipient
#         user.is_active = True
#         user.save()
#         token.used = True
#         token.save()

#         request.session['user_id'] = user.username
#         request.session.modified = True  
#         login(request, user)
        
#         return redirect('/questionnaire/?token= ' + str(token_value))
#     except Token.DoesNotExist:
#         return JsonResponse({'error': 'Invalid or expired token.'}, status=400)
    
    # token_value = request.GET.get('token')
    # if not token_value:
    #     return JsonResponse({'error': 'Token not found.'}, status=400)

    # # Validate the token
    # user = validate_token(token_value)
    # if not user:
    #     return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

    # # Log the user in (assuming you use Django's authentication system)
    # from django.contrib.auth import login
    # login(request, user)

    # # Redirect to the next step (e.g., questionnaire)
    # return redirect('/questionnaire/?token=' + str(token_value))

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to a dashboard or home page after login
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

    return render(request, 'login.html')

def login_with_token(request):
    token_value = request.GET.get('token')
    user = validate_token(token_value)
    if user is not None:
        login(request, user)
        return redirect('dashboard')  # Redirect to the dashboard or any authenticated page
    return JsonResponse({'error': 'Invalid token'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('login') 

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

@login_required
def dashboard(request):
    current_time = get_current_time()
    # user = request.user
    # participant = get_object_or_404(Participant, user=user)
    participant, created = Participant.objects.get_or_create(
        user=request.user,
        defaults={
            'enrollment_date': timezone.now().date(),
            'code_entered': False
        }
    )
    current_date = timezone.now().date()
    
    day_11 = participant.enrollment_date + timedelta(days=0)
    day_21 = participant.enrollment_date + timedelta(days=1)
    
    within_wave1_period = day_11 <= current_date <= day_21

    context = {
        'user': request.user,
        'progress': participant,
        'within_wave1_period': within_wave1_period,
        'code_error': request.GET.get('code_error', None),
        'days_until_start': (day_11 - current_date).days if current_date < day_11 else 0,
        'days_until_end': (day_21 - current_date).days if current_date <= day_21 else 0,
        'start_date': day_11,
        'end_date': day_21
    }
    return render(request, 'dashboard.html', context)

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

@login_required
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
                    'vuleson59@gmail.com',
                    [request.user.email, 'vuleson59@gmail.com'],
                    fail_silently=False,
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

@login_required
def code_success(request):
    return render(request, 'code_success.html')

@login_required
def code_failure(request):
    return render(request, 'code_failure.html')

# Add this function to be called by a scheduled task on Day 21
def check_code_entries():
    today = timezone.now().date()
    participants = Participant.objects.filter(
        enrollment_date=today - timedelta(days=20),
        code_entered=False
    )
    
    for participant in participants:
        # Send failure email (Information 14)
        send_mail(
            'Wave 1 Physical Activity Code Entry - Deadline Passed',
            'You did not enter the Wave 1 Physical Activity Code by Day 20. This task has now expired.',
            'from@yourdomain.com',  
            [participant.user.email],
            fail_silently=False,
        )

def generate_or_get_token(user):
    token, created = Token.objects.get_or_create(recipient=user)
    return token.token

def questionnaire_interest(request):
    if request.method == 'GET':
        return render(request, 'questionnaire_interest.html')
    elif request.method == 'POST':
        interested = request.POST.get('interested')
        if interested == 'no':
            return redirect('exit_screen_not_interested')
        return redirect('questionnaire')

#This function is used to send the email to the user in an automated schedule using celery
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

def intervention_access(request, participant_id):
    participant = Participant.objects.get(participant_id=participant_id)
    now = timezone.now()

    if participant.group == 0:
        access_message = "You will be given access to the intervention after Day 113."
    elif participant.group == 1:
        start_date = participant.entry_date + timedelta(days=29)
        end_date = participant.entry_date + timedelta(days=56)
        if start_date <= now <= end_date:
            access_message = "You have access to the intervention."
            # Track engagement
            participant.engagement_tracked = True
            participant.save()
        else:
            access_message = "Your access to the intervention is currently not available."
    else:
        access_message = "You have not been assigned to a group yet."

    return render(request, 'intervention_access.html', {'access_message': access_message})


@csrf_exempt
def questionnaire(request):
    token_value = request.GET.get('token')
    if not token_value:
        return JsonResponse({'error': 'Token not found in request.'}, status=400)
    
    token_value = token_value.strip()

    try:
        # Retrieve the token and user directly from the request
        token = Token.objects.get(token=token_value, used=True)
        user = token.recipient
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

    survey = Survey.objects.first()  # Assuming there is already at least one survey in the database
    if not survey:
        return JsonResponse({'error': 'No survey found.'}, status=404)
    
    if request.method == 'GET':
        survey = Survey.objects.first()
        if not survey:
            return JsonResponse({'error': 'No survey found.'}, status=404)     
        user_survey_progress, created = UserSurveyProgress.objects.get_or_create(user=user, survey=survey)
        if created:
            user_survey_progress.start_time = datetime.datetime.now()
            user_survey_progress.save()
        #     user=user,
        #     survey=survey,
        #     defaults={'start_time': datetime.datetime.now()}
        # )        
        questions = Question.objects.filter(survey=survey)
        return render(request, 'questionnaire.html', {'questions': questions, 'token': token_value})
    
    elif request.method == 'POST':
        survey = Survey.objects.first()
        if not survey:
            return JsonResponse({'error': 'No survey found.'}, status=404)
        # Get user using the token
        user_survey_progress, created = UserSurveyProgress.objects.get_or_create(user=user, survey=survey)

        # Save responses for each question
        questions = Question.objects.filter(survey=survey)
        for question in questions:
            answer = request.POST.get(f'question-{question.id}')
            if answer:
                Response.objects.create(
                    user=user,
                    question=question,
                    answer=answer
                )

        # Eligibility check logic
        data = {
            'age': request.POST.get('age'),
            'height': request.POST.get('height'),
            'weight': request.POST.get('weight'),
            'has_device': request.POST.get('has_device'),
            'not_enroll_other': request.POST.get('not_enroll_other'),
            'comply_monitoring': request.POST.get('comply_monitoring'),
            'respond_contacts': request.POST.get('respond_contacts'),
        }
        # Check eligibility using the updated `eligibility_check()` function
        is_eligible, eligibility_reason = eligibility_check(data)
        
        # Update the user survey progress
        user_survey_progress.eligible = is_eligible
        user_survey_progress.eligibility_reason = eligibility_reason
        user_survey_progress.end_time = datetime.datetime.now()  # Record end time
        user_survey_progress.survey_completed = True
        user_survey_progress.progress_percentage = 100  # Assuming survey completion means 100%
        user_survey_progress.save()
        # user_survey_progress, created = UserSurveyProgress.objects.get_or_create(user=user)
        # user_survey_progress.eligible = is_eligible
        # user_survey_progress.save()

        if not is_eligible:
            # Redirect to not eligible exit screen
            return redirect('exit_screen_not_eligible')

        # If eligible, proceed to consent form, keep passing the token
        return redirect(f'/consent-form/?token={token_value}')


def exit_screen_not_interested(request):
    if request.method == 'GET':
        return render(request, 'exit_screen_not_interested.html')


def exit_screen_not_eligible(request):
    return render(request, 'exit_screen_not_eligible.html')

def consent_form(request):
    token_value = request.GET.get('token')
    if not token_value:
        return JsonResponse({'error': 'Token not found in request.'}, status=400)
    
    try:
        # Retrieve the token and user directly 
        token = Token.objects.get(token=token_value, used=True)
        user = token.recipient
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

    if request.method == 'GET':
        return render(request, 'consent_form.html', {'token': token_value})

    elif request.method == 'POST':
        consent = request.POST.get('consent')
        if consent == 'yes':
            # User day 1
            user_survey_progress, created = UserSurveyProgress.objects.get_or_create(user=user)
            # user_survey_progress.day_1 = timezone.now().date()
            user_survey_progress.day_1 = datetime.datetime.now()
            user_survey_progress.save()

            # Send email for wave 1 (information 9)
            send_wave_1_email(user)
            
            # Proceed to the waiting screen, keep passing the token
            return redirect(f'/waiting-screen/?token={token_value}')
        return redirect('exit_screen_not_interested')

# views.py

def user_data_report(request):
    users = User.objects.all()
    user_data = []

    for user in users:
        survey_progress = UserSurveyProgress.objects.filter(user=user).first()
        responses = Response.objects.filter(user=user)

        user_data.append({
            'user': user,
            'survey_progress': survey_progress,
            'responses': responses,
        })

    return render(request, 'user_data_report.html', {'user_data': user_data})

# def consent_form(request):
#     if request.method == 'GET':
#         return render(request, 'consent_form.html')
#     elif request.method == 'POST':
#         consent = request.POST.get('consent')
#         if consent == 'yes':
#             return redirect('waiting_screen')
#         return redirect('exit_screen_not_interested')

def waiting_screen(request):
    if request.method == 'GET':
        return render(request, 'waiting_screen.html')