#track user progress through survey and then (maybe) send an email when the survey is completed
from django.shortcuts import render, redirect
from django.utils import timezone
from testpas.models import Survey, Question, Response, UserSurveyProgress
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

def send_completion_email(user_email, survey):
    message = Mail(
        from_email='no-reply@example.com',
        to_emails=user_email,
        subject='Survey Completed',
        html_content=f'Thank you for completing the survey: {survey.title}.')
    sg = SendGridAPIClient("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")
    sg.send(message)
