from django.contrib import admin
from .models import Quiz_Model
from account.models import Profile_Model



class Quiz_Admin(admin.ModelAdmin):
    list_display = ('quiz_name', 'user')


class Profile_Admin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'current_quiz_number')


admin.site.register(Quiz_Model, Quiz_Admin)
admin.site.register(Profile_Model, Profile_Admin)