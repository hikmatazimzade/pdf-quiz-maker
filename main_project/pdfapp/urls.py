from django.urls import path
from .import views
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('', views.home, name = 'home'),
    path('home', views.home, name = 'home'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('quiz/<slug:slug>', views.quiz, name = 'quiz'),
    path('create_quiz', views.create_quiz, name = 'create_quiz'),
    path('quiz_choice', views.quiz_choice, name = 'quiz_choice'),
    path('edit_quiz/<slug:slug>', views.edit_quiz, name = 'edit_quiz'),
    path('delete_quiz/<slug:slug>', views.delete_quiz, name = 'delete_quiz'),
    path('about', views.about, name = 'about'),
    #path('buy_me_coffee', views.buy_me_coffee, name = 'buy_me_coffee'),
    path('contact', views.contact, name = 'contact'),
    path('user_guide', views.user_guide, name = 'user_guide'),
    path("load_page", views.load_page, name = "load_page"),
    path('check_quiz_status', views.check_quiz_status, name='check_quiz_status'),
    path('success_quiz_choice', views.success_quiz_choice, name = 'success_quiz_choice'),
    path("create_error", views.create_error, name = "create_error")
]