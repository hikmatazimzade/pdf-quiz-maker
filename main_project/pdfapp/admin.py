from django.contrib import admin
from .models import QuizModel
from account.models import ProfileModel



class Quiz_Admin(admin.ModelAdmin):
    list_display = ('quiz_name', 'user')


class Profile_Admin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'current_quiz_number')


admin.site.register(QuizModel, Quiz_Admin)
admin.site.register(ProfileModel, Profile_Admin)