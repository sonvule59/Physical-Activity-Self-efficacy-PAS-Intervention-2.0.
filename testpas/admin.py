# testpas/admin.py
from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Participant, Survey, UserSurveyProgress, Response, EmailTemplate

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('participant_id', 'user', 'enrollment_date', 'code_entered', 'wave3_code_entered', 'group')
    actions = ['export_study_data']

    def export_study_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pas_study_data.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Participant ID', 'Username', 'Email', 'Phone Number', 'Enrollment Date', 'Eligible', 'Consent Given',
            'Decline Reason', 'Survey Progress (%)', 'Survey Responses', 'Wave 1 Code Entered', 'Wave 1 Code Entry Date',
            'Group', 'Intervention Start', 'Intervention End', 'Wave 3 Code Entered', 'Wave 3 Code Entry Date'
        ])
        for participant in queryset:
            progress = UserSurveyProgress.objects.filter(user=participant.user).first()
            responses = Response.objects.filter(user=participant.user).values_list('question', 'answer')
            response_str = '; '.join([f"{q}: {a}" for q, a in responses]) if responses else 'N/A'
            progress_percentage = progress.progress if progress and progress.progress is not None else 'N/A'

            writer.writerow([
                participant.participant_id,
                participant.user.username,
                participant.user.email,
                participant.phone_number,
                participant.enrollment_date,
                progress.eligible if progress else 'N/A',
                progress.consent_given if progress else 'N/A',
                progress.decline_reason if progress and not progress.consent_given else '',
                progress_percentage,  # New column for survey progress
                response_str,         # Survey answers
                participant.code_entered,
                participant.code_entry_date,
                participant.group,
                participant.intervention_start_date,
                participant.intervention_end_date,
                participant.wave3_code_entered,
                participant.wave3_code_entry_date
            ])
        return response

    export_study_data.short_description = "Export PAS study data (Info 2-6, 11, 15, 22)"

admin.site.register(Survey)
admin.site.register(UserSurveyProgress)
admin.site.register(Response)
admin.site.register(EmailTemplate)

# admin.site.register(Participant, ParticipantAdmin)
# admin.site.register(UserSurveyProgress)
# admin.site.register(Survey)
# admin.site.register(Question)
# admin.site.register(EmailTemplate)
# admin.site.register(EmailContent)
# admin.site.register(ParticipantEntry)

