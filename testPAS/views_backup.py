#track user progress through survey and then (maybe) send an email when the survey is completed
from smtplib import SMTPException
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from testpas.models import Survey, Question, Response, UserSurveyProgress
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
import logging
# from testpas.utils import EmailService, generate_token  
from .models import Token
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import EmailService, generate_token  
from testpas.models import Token
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
import uuid


@csrf_exempt
def create_account(request):
    
    if request.method == 'POST':
        try:
            # Debug: Print request body to see the data
            print("Request Body: ", request.body)
            data = json.loads(request.body)

            # Extract and validate fields
            registration_code = data.get('registration-code', '').strip().lower()
            user_id = data.get('user-id', '').strip()
            password = data.get('password', '')
            password_confirmation = data.get('password-confirmation', '')
            email = data.get('email', '').strip().lower()
            phone_number = data.get('phone-number', '').strip()

            # Check if registration code is missing or incorrect
            if registration_code != 'wavepa':
                return JsonResponse({'error': 'Invalid registration code.'}, status=400)

            # Verify passwords match
            if password != password_confirmation:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            # Check if user already exists
            if User.objects.filter(username=user_id).exists():
                return JsonResponse({'error': 'User ID already taken.'}, status=400)

            # Create user
            user = User.objects.create_user(username=user_id, password=password, email=email)
            user.is_active = False  # Set user to inactive until email confirmation
            user.save()

            # Debug: Verify user creation
            print(f"User instance created: {user}, ID: {user.id}, Email: {user.email}")

            # Generate token for the user
            token_value = str(uuid.uuid4())  # Generate a random token value

            # Create and assign the token to the user (recipient must be a User instance)
            Token.objects.create(recipient=user, token=token_value)

            # Send confirmation email with token
            confirmation_link = f"http://yourdomain.com/confirm-account/?token={token_value}"
            send_mail(
                'Confirm Your Account',
                f'Thank you for registering. Please confirm your account by clicking the link below:\n\n{confirmation_link}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print(f"Exception occurred: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return render(request, 'create_account.html')

# Account confirmation view
def confirm_account(request):
    token_value = request.GET.get('token')
    try:
        token = Token.objects.get(token=token_value, used=False)
        user = token.recipient
        user.is_active = True  # Activate the user account
        user.save()
        token.used = True
        token.save()
        return redirect('questionnaire_interest')  # Redirect to questionnaire interest page
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

# Questionnaire interest view
def questionnaire_interest(request):
    if request.method == 'GET':
        return render(request, 'questionnaire_interest.html')
    elif request.method == 'POST':
        interested = request.POST.get('interested')
        if interested == 'no':
            return redirect('exit_screen')
        return redirect('questionnaire')
# Eligibility check function

def eligibility_check(user, data):
    # Age eligibility: Age must be between 18 and 64 (inclusive)
    age = int(data.get('age'))
    if age < 18 or age > 64:
        return False, 'Age requirement not met. Must be between 18 and 64 years.'

    return True

@csrf_exempt
def questionnaire(request):
    if request.method == 'GET':
        # Pass the user_id to the form template, assuming it's stored in session
        user_id = request.session.get('user_id')
        return render(request, 'questionnaire.html', {'user_id': user_id})

    elif request.method == 'POST':
        # Get questionnaire data from request.POST
        data = {
            'age': request.POST.get('age'),
            'height': request.POST.get('height'),
            'weight': request.POST.get('weight'),
            'has_device': request.POST.get('has_device'),
            'not_enroll_other': request.POST.get('not_enroll_other'),
            'comply_monitoring': request.POST.get('comply_monitoring'),
            'respond_contacts': request.POST.get('respond_contacts'),
        }

        # Get user using the user-id from form data
        user_id = request.POST.get('user-id')
        user = get_object_or_404(User, username=user_id)

        # Check eligibility using the updated `eligibility_check()` function
        is_eligible, message = eligibility_check(data)

        if not is_eligible:
            # Send ineligibility email
            send_mail(
                'Eligibility Notification',
                f'We regret to inform you that you are not eligible to participate in this program due to the following reason: {message}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            return redirect('exit_screen')

        # If eligible, proceed to consent form
        return redirect('consent_form')


  
# @csrf_exempt
# def questionnaire(request):
#     if request.method == 'GET':
#         return render(request, 'questionnaire.html')
#     elif request.method == 'POST':
#         # Get questionnaire data from request
#         data = json.loads(request.body)
#         # Get user
#         user_id = data.get('user-id')
#         user = get_object_or_404(User, username=user_id)
#         # Check eligibility
#         is_eligible, message = eligibility_check(data)

#         if not is_eligible:
#             # Send ineligibility email
#             send_mail(
#                 'Eligibility Notification',
#                 f'We regret to inform you that you are not eligible to participate in this program due to the following reason: {message}',
#                 'noreply@example.com',
#                 [user.email],
#                 fail_silently=False,
#             )
#             return redirect('exit_screen')

#         return redirect('consent_form')




# Consent form view
def consent_form(request):
    if request.method == 'GET':
        return render(request, 'consent_form.html')
    elif request.method == 'POST':
        consent = request.POST.get('consent')
        if consent == 'yes':
            # Mark the consent date as Day 1
            # Placeholder logic: Save consent date to user's profile (needs profile model update)
            return redirect('waiting_screen')
        return redirect('exit_screen')

# Exit screen view
def exit_screen(request):
    return render(request, 'exit_screen.html')

# Waiting screen view
def waiting_screen(request):
    return render(request, 'waiting_screen.html')





def index(request):
    surveys = Survey.objects.all()
    return render(request, 'index.html', {'surveys': surveys})

# def start_survey(request, survey_id):
#     survey = Survey.objects.get(pk=survey_id)
#     if request.method == 'POST':
#         progress, _ = UserSurveyProgress.objects.get_or_create(user=request.user, survey=survey)
#         progress.start_time = timezone.now()
#         progress.save()
#         return redirect('survey_questions', survey_id=survey_id)
    
#     return render(request, 'start_survey.html', {'survey': survey})

# def survey_questions(request, survey_id):
#     survey = Survey.objects.get(pk=survey_id)
#     progress = UserSurveyProgress.objects.get(user=request.user, survey=survey)

#     if request.method == 'POST':
#         question_id = request.POST.get('question_id')
#         answer = request.POST.get('answer')
#         question = Question.objects.get(pk=question_id)
#         Response.objects.create(user=request.user, question=question, answer=answer)
        
#         # Track progress
#         progress.progress += 1
#         if progress.progress == survey.questions.count():
#             progress.end_time = timezone.now()
#         progress.save()

#         return redirect('next_question', survey_id=survey_id)

#     unanswered = survey.questions.exclude(response__user=request.user).first()
#     if unanswered:
#         return render(request, 'question.html', {'question': unanswered})
    
#     return redirect('survey_complete', survey_id=survey_id)

# def survey_complete(request, survey_id):
#     survey = Survey.objects.get(pk=survey_id)
#     progress = UserSurveyProgress.objects.get(user=request.user, survey=survey)
    
#     # Send completion email
#     send_completion_email(request.user.email, survey)
    
#     return render(request, 'survey_complete.html', {'survey': survey, 'progress': progress})

# @csrf_exempt
# def send_token_email(request):
#     if request.method == 'POST':
#         try:
#             # Debug: Print incoming request data
#             print("Request body:", request.body)
#             data = json.loads(request.body)

#             email = data.get('email')
#             if not email:
#                 return JsonResponse({'error': 'Email is required'}, status=400)

#             # Debug: Generating the token
#             print(f"Generating token for email: {email}")
#             token_value = generate_token()

#             # Debug: Saving the token to the database
#             print(f"Saving token {token_value} to database for {email}")
#             Token.objects.create(recipient=email, token=token_value, created_at=timezone.now())

#             # Configure and use the email service
#             email_service = EmailService(
#                 smtp_server="smtp.gmail.com",
#                 smtp_port=587,
#                 smtp_user="projectpas2024@gmail.com",
#                 smtp_password="ybmp kmbc xxve lghn "
#             )

#             # Debug: Sending the email
#             print(f"Sending token email to {email}")
#             email_service.send_email(email, "Your Token", f"Your token is: {token_value}")

#             return JsonResponse({'message': 'Token sent successfully'})

#         except SMTPException as smtp_err:
#             print(f"SMTPException occurred: {str(smtp_err)}")
#             return JsonResponse({'error': f'SMTP error: {str(smtp_err)}'}, status=500)

#         except json.JSONDecodeError:
#             print("Error: Failed to parse JSON request body.")
#             return JsonResponse({'error': 'Invalid JSON format'}, status=400)

#         except Exception as e:
#             print(f"Exception occurred: {str(e)}")
#             return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# def send_completion_email(user_email, survey):
#     message = Mail(
#         from_email='no-reply@example.com',
#         to_emails=user_email,
#         subject='Survey Completed',
#         html_content=f'Thank you for completing the survey: {survey.title}.')
#     sg = SendGridAPIClient("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")
#     sg.send(message)

# # Configure logging
# logger = logging.getLogger(__name__)

# def eligibility_check(user):

#     return True

# # # Inside create_account view
# # is_eligible = eligibility_check(user)

# # if is_eligible:
# #     eligibility_message = "Congratulations! You have passed the eligibility test."
# # else:
# #     eligibility_message = "Unfortunately, you did not pass the eligibility test at this time."

# # # Placeholder eligibility check function (add your logic here)
# # def eligibility_check(user):
# #     # Add logic to determine eligibility
# #     return True

# # Inside create_account view
# @csrf_exempt
# def create_account(request):
#     if request.method == 'GET':
#         return render(request, 'create_account.html')
#     elif request.method == 'POST':
#         try:
#             # Debug: print request body to see the data
#             print("Request Body: ", request.body)
#             data = json.loads(request.body)

#             # Extract and validate fields
#             registration_code = data.get('registration-code', '').strip().lower()
#             user_id = data.get('user-id', '').strip()
#             password = data.get('password', '')
#             password_confirmation = data.get('password-confirmation', '')
#             email = data.get('email', '').strip().lower()
#             phone_number = data.get('phone-number', '').strip()

#             # Check if registration code is missing or incorrect
#             if registration_code != 'wavepa':
#                 return JsonResponse({'error': 'Invalid registration code.'}, status=400)

#             # Verify passwords match
#             if password != password_confirmation:
#                 return JsonResponse({'error': 'Passwords do not match.'}, status=400)

#             # Check if user already exists
#             if User.objects.filter(username=user_id).exists():
#                 return JsonResponse({'error': 'User ID already taken.'}, status=400)

#             # Create user
#             user = User.objects.create_user(username=user_id, password=password, email=email)
#             user.is_active = False  # Set user to inactive until email confirmation
#             user.save()

#             # Create a test user
#             user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
#             print(f"User created: {user}, ID: {user.id}")

#             # Generate a token for this user
#             token_value = str(uuid.uuid4())
#             user = get_object_or_404(User, id=user.id)
#             Token.objects.create(recipient=user, token=token_value)
#             print(f"Token created successfully for user {user.username}")
            

#             # # Generate token for the user
#             # token_value = str(uuid.uuid4())  # Generate a random token value
#             # Token.objects.create(recipient=user, token=token_value)

#             # Check eligibility
#             is_eligible = eligibility_check(user)
#             if is_eligible:
#                 eligibility_message = "Congratulations! You have passed the eligibility test."
#             else:
#                 eligibility_message = "Unfortunately, you did not pass the eligibility test at this time."

#             # Send confirmation email with token
#             send_mail(
#                 'Confirm Your Account',
#                 f'{eligibility_message}\n\nPlease confirm your account by clicking the link below.\n\nYour token: {token_value}',
#                 'noreply@example.com',
#                 [email],
#                 fail_silently=False,
#             )

#             return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

#         except Exception as e:
#             logger.error(f"Exception occurred: {str(e)}")  # Debug line to check the exact error
#             return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

#     return render(request, 'create_account.html')



# # @csrf_exempt
# # def create_account(request):
# #     if request.method == 'POST':
# #         try:
# #             # Debug: print request body to see the data
# #             print("Request Body: ", request.body)
# #             data = json.loads(request.body)

# #             # Extract and validate fields
# #             registration_code = data.get('registration-code', '').strip().lower()
# #             user_id = data.get('user-id', '').strip()
# #             password = data.get('password', '')
# #             password_confirmation = data.get('password-confirmation', '')
# #             email = data.get('email', '').strip().lower()
# #             phone_number = data.get('phone-number', '').strip()

# #             # Check if registration code is missing or incorrect
# #             if registration_code != 'wavepa':
# #                 return JsonResponse({'error': 'Invalid registration code.'}, status=400)

# #             # Verify passwords match
# #             if password != password_confirmation:
# #                 return JsonResponse({'error': 'Passwords do not match.'}, status=400)

# #             # Check if user already exists
# #             if User.objects.filter(username=user_id).exists():
# #                 return JsonResponse({'error': 'User ID already taken.'}, status=400)

# #             # Create user
# #             user = User.objects.create_user(username=user_id, password=password, email=email)
# #             user.is_active = False  # Set user to inactive until email confirmation
# #             user.save()

# #             # Generate token for the user
# #             token_value = str(uuid.uuid4())  # Generate a random token value
# #             Token.objects.create(recipient=user, token=token_value)

# #             # Send confirmation email with token
# #             send_mail(
# #                 'Confirm Your Account',
# #                 f'Thank you for registering. Please confirm your account by clicking the link below.\n\nYour token: {token_value}',
# #                 'noreply@example.com',
# #                 [email],
# #                 fail_silently=False,
# #             )

# #             return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})

# #         except json.JSONDecodeError:
# #             return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

# #         except Exception as e:
# #             print(f"Exception occurred: {str(e)}")  
# #             return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

# #     return render(request, 'create_account.html')

# # @csrf_exempt
# # def create_account(request):
# #     if request.method == 'GET':
# #         return render(request, 'create_account.html')
# #     elif request.method == 'POST':
# #         try:
# #             data = json.loads(request.body)
# #             registration_code = data.get('registration-code').strip().lower()
# #             user_id = data.get('user-id').strip()
# #             password = data.get('password')
# #             password_confirmation = data.get('password-confirmation')
# #             email = data.get('email').strip().lower()
# #             phone_number = data.get('phone-number').strip()

# #             # Verify registration code
# #             if registration_code != 'wavepa':
# #                 return JsonResponse({'error': 'Invalid registration code.'}, status=400)

# #             # Verify passwords match
# #             if password != password_confirmation:
# #                 return JsonResponse({'error': 'Passwords do not match.'}, status=400)

# #             # Check if user already exists
# #             if User.objects.filter(username=user_id).exists():
# #                 return JsonResponse({'error': 'User ID already taken.'}, status=400)

# #             # Create user
# #             user = User.objects.create_user(username=user_id, password=password, email=email)
# #             user.is_active = False  # Mark the user as inactive until email confirmation
# #             user.save()

# #             # Send confirmation email
# #             try:
# #                 send_mail(
# #                     'Confirm Your Account',
# #                     'Thank you for registering. Please confirm your account by clicking the link below.',
# #                     'noreply@example.com',
# #                     [email],
# #                     fail_silently=False,
# #                 )
# #                 return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})
# #             except Exception as e:
# #                 return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)
# #         except json.JSONDecodeError:
# #             return JsonResponse({'error': 'Invalid JSON format'}, status=400)
# #         except Exception as e:
# #             return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
# #     else:
# #         return JsonResponse({'error': 'Invalid request method'}, status=405)
