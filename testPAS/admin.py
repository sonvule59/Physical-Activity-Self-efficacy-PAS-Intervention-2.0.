from django.contrib import admin
from .models import UserSurveyProgress, Token, Response, Survey

# Register your models here
admin.site.register(UserSurveyProgress)
admin.site.register(Token)
admin.site.register(Response)
admin.site.register(Survey)
