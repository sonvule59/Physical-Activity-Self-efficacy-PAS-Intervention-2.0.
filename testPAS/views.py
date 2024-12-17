# views.py

import datetime
from time import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import Survey, Question, Response, UserSurveyProgress, Token, User, Survey
from .utils import validate_token
import uuid
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
import os
from .models import Participant
from .forms import CodeEntryForm
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
        [user.email, 'vuleson59@gmail.com'],
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

def confirm_account(request):
    token_value = request.GET.get('token')
    try:
        token = Token.objects.get(token=token_value, used=False)
        user = token.recipient
        user.is_active = True
        user.save()
        token.used = True
        token.save()

        request.session['user_id'] = user.username
        request.session.modified = True  
        login(request, user)
        
        return redirect('/questionnaire/?token= ' + str(token_value))
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)
    
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

# @login_required
def dashboard(request):
    # user = request.user
    # participant = get_object_or_404(Participant, user=user)
    # current_date = timezone.now().date()
    # day_11 = participant.enrollment_date + timezone.timedelta(days=10)
    # day_21 = participant.enrollment_date + timezone.timedelta(days=20)
    # within_wave1_period = day_11 <= current_date <= day_21

    # context = {
    #     'user': user,
    #     'progress': participant,
    #     'within_wave1_period': within_wave1_period,
    #     'code_error': request.GET.get('code_error', None),
    # }
    return render(request, 'dashboard.html')

# @login_required
# def enter_code(request):
#     participant = Participant.objects.get(user=request.user)
#     current_date = timezone.now().date()
#     day_21 = participant.enrollment_date + timezone.timedelta(days=20)

#     if current_date > day_21:
#         return redirect('code_failure')

#     if request.method == 'POST':
#         form = CodeEntryForm(request.POST)
#         if form.is_valid():
#             code = form.cleaned_data['code'].strip().lower()
#             if code == 'wavepa':
#                 participant.code_entered = True
#                 participant.code_entry_date = current_date
#                 participant.save()
#                 send_mail(
#                     'Code Entered Successfully',
#                     'You have successfully entered the Wave 1 Physical Activity Code.',
#                     'from@example.com',
#                     [request.user.email],
#                     fail_silently=False,
#                 )
#                 return redirect('code_success')
#             else:
#                 return render(request, 'participants/enter_code.html', {'form': form, 'error': 'Incorrect code. Please try again.'})
#     else:
#         form = CodeEntryForm()

#     return render(request, 'participants/enter_code.html', {'form': form})

# @login_required
# def code_success(request):
#     return render(request, 'participants/code_success.html')

# @login_required
# def code_failure(request):
#     participant = Participant.objects.get(user=request.user)
#     if not participant.code_entered and timezone.now().date() > participant.enrollment_date + timezone.timedelta(days=20):
#         send_mail(
#             'Code Entry Failed',
#             'You did not enter the Wave 1 Physical Activity Code by Day 20.',
#             'from@example.com',
#             [request.user.email],
#             fail_silently=False,
#         )
#     return render(request, 'participants/code_failure.html')




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