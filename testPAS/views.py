#track user progress through survey and then (maybe) send an email when the survey is completed
from smtplib import SMTPException
from django.core.mail import send_mail
from django.shortcuts import render, redirect
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
from .models import Token
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 


# class HelloView(APIView):
#     permission_classes = (IsAuthenticated,)             # Require authentication

#     def get(self, request):
#         content = {'message': 'Hello, World!'}
#         return Response(content)
    
def index(request):
    surveys = Survey.objects.all()
    return render(request, 'index.html', {'surveys': surveys})

def start_survey(request, survey_id):
    survey = Survey.objects.get(pk=survey_id)
    if request.method == 'POST':
        progress, _ = UserSurveyProgress.objects.get_or_create(user=request.user, survey=survey)
        progress.start_time = timezone.now()
        progress.save()
        return redirect('survey_questions', survey_id=survey_id)
    
    return render(request, 'start_survey.html', {'survey': survey})

def survey_questions(request, survey_id):
    survey = Survey.objects.get(pk=survey_id)
    progress = UserSurveyProgress.objects.get(user=request.user, survey=survey)

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        question = Question.objects.get(pk=question_id)
        Response.objects.create(user=request.user, question=question, answer=answer)
        
        # Track progress
        progress.progress += 1
        if progress.progress == survey.questions.count():
            progress.end_time = timezone.now()
        progress.save()

        return redirect('next_question', survey_id=survey_id)

    unanswered = survey.questions.exclude(response__user=request.user).first()
    if unanswered:
        return render(request, 'question.html', {'question': unanswered})
    
    return redirect('survey_complete', survey_id=survey_id)

def survey_complete(request, survey_id):
    survey = Survey.objects.get(pk=survey_id)
    progress = UserSurveyProgress.objects.get(user=request.user, survey=survey)
    
    # Send completion email
    send_completion_email(request.user.email, survey)
    
    return render(request, 'survey_complete.html', {'survey': survey, 'progress': progress})

@csrf_exempt
def send_token_email(request):
    if request.method == 'POST':
        try:
            # Debug: Print incoming request data
            print("Request body:", request.body)
            data = json.loads(request.body)

            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)

            # Debug: Generating the token
            print(f"Generating token for email: {email}")
            token_value = generate_token()

            # Debug: Saving the token to the database
            print(f"Saving token {token_value} to database for {email}")
            Token.objects.create(recipient=email, token=token_value, created_at=timezone.now())

            # Configure and use the email service
            email_service = EmailService(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                smtp_user="projectpas2024@gmail.com",
                smtp_password="ybmp kmbc xxve lghn "
            )

            # Debug: Sending the email
            print(f"Sending token email to {email}")
            email_service.send_email(email, "Your Token", f"Your token is: {token_value}")

            return JsonResponse({'message': 'Token sent successfully'})

        except SMTPException as smtp_err:
            print(f"SMTPException occurred: {str(smtp_err)}")
            return JsonResponse({'error': f'SMTP error: {str(smtp_err)}'}, status=500)

        except json.JSONDecodeError:
            print("Error: Failed to parse JSON request body.")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def send_completion_email(user_email, survey):
    message = Mail(
        from_email='no-reply@example.com',
        to_emails=user_email,
        subject='Survey Completed',
        html_content=f'Thank you for completing the survey: {survey.title}.')
    sg = SendGridAPIClient("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")
    sg.send(message)

# Configure logging
logger = logging.getLogger(__name__)
@csrf_exempt
def create_account(request):
    if request.method == 'GET':
        return render(request, 'create_account.html')
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            registration_code = data.get('registration-code').strip().lower()
            user_id = data.get('user-id').strip()
            password = data.get('password')
            password_confirmation = data.get('password-confirmation')
            email = data.get('email').strip().lower()
            phone_number = data.get('phone-number').strip()

            # Verify registration code
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
            user.is_active = False  # Mark the user as inactive until email confirmation
            user.save()

            # Send confirmation email
            try:
                send_mail(
                    'Confirm Your Account',
                    'Thank you for registering. Please confirm your account by clicking the link below.',
                    'noreply@example.com',
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})
            except Exception as e:
                return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
# def create_account(request):
#     if request.method == 'GET':
#         return render(request, 'create_account.html')
#     elif request.method == 'POST':
#         registration_code = request.POST.get('registration-code').strip().lower()
#         user_id = request.POST.get('user-id').strip()
#         password = request.POST.get('password')
#         password_confirmation = request.POST.get('password-confirmation')
#         email = request.POST.get('email').strip().lower()
#         phone_number = request.POST.get('phone-number').strip()

#         # Verify registration code
#         if registration_code != 'wavepa':
#             return JsonResponse({'error': 'Invalid registration code.'}, status=400)

#         # Verify passwords match
#         if password != password_confirmation:
#             return JsonResponse({'error': 'Passwords do not match.'}, status=400)

#         # Check if user already exists
#         if User.objects.filter(username=user_id).exists():
#             return JsonResponse({'error': 'User ID already taken.'}, status=400)

#         # Create user
#         user = User.objects.create_user(username=user_id, password=password, email=email)
#         user.is_active = False  # Mark the user as inactive until email confirmation
#         user.save()

#         # Send confirmation email
#         try:
#             send_mail(
#                 'Confirm Your Account',
#                 'Thank you for registering. Please confirm your account by clicking the link below.',
#                 'noreply@example.com',
#                 [email],
#                 fail_silently=False,
#             )
#             return JsonResponse({'message': 'Account created successfully. Please check your email to confirm your account.'})
#         except Exception as e:
#             return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)

#     return render(request, 'create_account.html')
  