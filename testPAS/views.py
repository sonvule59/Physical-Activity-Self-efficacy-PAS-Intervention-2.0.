# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Token
import uuid
from django.contrib.auth import login
from django.conf import settings

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
        request.session.modified = True  # Ensure session is saved
        login(request, user)
        
        return redirect(f'/questionnaire/?token={token_value}')
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)
        

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
    
    try:
        # Retrieve the token and user directly from the request
        token = Token.objects.get(token=token_value, used=True)
        user = token.recipient
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

    if request.method == 'GET':
        return render(request, 'questionnaire.html', {'token': token_value})

    elif request.method == 'POST':
        # Proceed with processing the form data
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
        is_eligible, message = eligibility_check(data)

        if not is_eligible:
            # Redirect to not eligible exit screen
            return redirect('exit_screen_not_eligible')

        # If eligible, proceed to consent form, keep passing the token
        return redirect(f'/consent-form/?token={token_value}')

# @csrf_exempt
# def questionnaire(request):
#     if request.method == 'GET':
#         # Ensure user_id exists in session
#         user_id = request.session.get('user_id')
#         if not user_id:
#             return JsonResponse({'error': 'User not found in session. Please confirm your account first.'}, status=400)

#         return render(request, 'questionnaire.html')

#     elif request.method == 'POST':
#         # Get user using the user ID stored in the session
#         user_id = request.session.get('user_id')
#         if not user_id:
#             return JsonResponse({'error': 'User not found in session.'}, status=400)

#         # Proceed with processing the form data
#         data = {
#             'age': request.POST.get('age'),
#             'height': request.POST.get('height'),
#             'weight': request.POST.get('weight'),
#             'has_device': request.POST.get('has_device'),
#             'not_enroll_other': request.POST.get('not_enroll_other'),
#             'comply_monitoring': request.POST.get('comply_monitoring'),
#             'respond_contacts': request.POST.get('respond_contacts'),
#         }

#         user = get_object_or_404(User, pk=user_id)

#         # Check eligibility using the updated `eligibility_check()` function
#         is_eligible, message = eligibility_check(data)

#         if not is_eligible:
#             # Send ineligibility email (optional, as per your request)
#             return redirect('exit_screen_not_eligible')

#         # If eligible, proceed to consent form
#         return redirect('consent_form')


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
        # Retrieve the token and user directly from the request
        token = Token.objects.get(token=token_value, used=True)
        user = token.recipient
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired token.'}, status=400)

    if request.method == 'GET':
        return render(request, 'consent_form.html', {'token': token_value})

    elif request.method == 'POST':
        consent = request.POST.get('consent')
        if consent == 'yes':
            # Proceed to the waiting screen, keep passing the token
            return redirect(f'/waiting-screen/?token={token_value}')
        return redirect('exit_screen_not_interested')

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