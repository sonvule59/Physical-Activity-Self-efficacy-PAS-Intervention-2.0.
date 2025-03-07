from django.contrib import admin
from .models import *
from django.db import models
from django.contrib.auth.models import User
from .models import EmailTemplate, Participant, UserSurveyProgress, Survey  # Add other models as needed

# testpas/admin.py
from django.contrib import admin
from .models import UserSurveyProgress, Participant, Survey, Question, Response
import csv
from django.http import HttpResponse

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('participant_id', 'user', 'enrollment_date', 'code_entered', 'wave3_code_entered')
    actions = ['export_study_data']
    def export_study_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="study_data.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Participant ID', 'Username', 'Email', 'Enrollment Date', 'Eligible', 'Consent Given',
            'Wave 1 Code Entered', 'Wave 3 Code Entered', 'Wave 3 Code Entry Date', 'Survey Responses'
        ])
        for participant in queryset:
            progress = UserSurveyProgress.objects.filter(user=participant.user).first()
            responses = Response.objects.filter(user=participant.user).values_list('answer', flat=True)
            writer.writerow([
                participant.participant_id,
                participant.user.username,
                participant.user.email,
                participant.enrollment_date,
                progress.eligible if progress else 'N/A',
                progress.consent_given if progress else 'N/A',
                participant.code_entered,
                participant.wave3_code_entered,
                participant.wave3_code_entry_date,
                ';'.join(responses)
            ])
        return response
    export_study_data.short_description = "Export study data (Info 2-6, 11, 15, 22)"

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(UserSurveyProgress)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(EmailTemplate)
admin.site.register(EmailContent)
admin.site.register(ParticipantEntry)

