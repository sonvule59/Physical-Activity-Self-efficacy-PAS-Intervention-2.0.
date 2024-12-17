from django.contrib import admin
from .models import UserSurveyProgress, Response, Survey, Question, Token, Participant
from django.db import models
from django.contrib.auth.models import User
# from django.utils import timezone

# @admin.register(Participant)
# class ParticipantAdmin(admin.ModelAdmin):
#     list_display = ('user', 'enrollment_date', 'code_entered', 'code_entry_date')
#     search_fields = ('user__username',)
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'token', 'used', 'created_at')
    actions = ['reset_token']

    def reset_token(self, request, queryset):
        for token in queryset:
            token.used = False
            token.save()
        self.message_user(request, "Selected tokens have been reset.")
    reset_token.short_description = "Reset selected tokens"


# Register your models here
admin.site.register(UserSurveyProgress)
admin.site.register(Response)
admin.site.register(Survey)
admin.site.register(Question)