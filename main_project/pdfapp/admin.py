from django.contrib import admin

from pdfapp.models import QuizModel
from account.models import ProfileModel


class Quiz_Admin(admin.ModelAdmin):
    list_display = ('quiz_name', 'user', 'max_test_number')
    list_display_links = ('quiz_name',)
    search_fields = ('quiz_name',)
    autocomplete_fields = ('user',)
    prepopulated_fields = {"slug": ("quiz_name",),}
    readonly_fields = ('slug',)


class Profile_Admin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'current_quiz_number')
    autocomplete_fields = ('user',)


admin.site.register(QuizModel, Quiz_Admin)
admin.site.register(ProfileModel, Profile_Admin)