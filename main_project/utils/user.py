import logging

from django.core.cache import cache

from pdfapp.models import QuizModel

logger = logging.getLogger(__name__)


def edit_user_quiz(user_quiz: QuizModel, quiz_name: str, test_number: int,
        show_number: bool, shuffle_variant: int,
        slider_1: int, slider_2: int) -> None:
    user_quiz.quiz_name = quiz_name
    user_quiz.test_number = test_number
    user_quiz.show_number = show_number
    user_quiz.shuffle_variant = shuffle_variant
    user_quiz.first_boundary = slider_1
    user_quiz.last_boundary = slider_2
    user_quiz.save()


def edit_user_cache(request, slug: str, quiz_settings: dict, quiz_params: dict) -> None:
    cache_name = str(request.user.id) + slug
    quiz_settings["quiz_name"] = quiz_params["quiz_name"]
    quiz_settings["test_number"] = quiz_params["test_number"]
    quiz_settings["show_number"] = quiz_params["show_number"]
    quiz_settings["shuffle_variant"] = quiz_params["shuffle_variant"]
    quiz_settings["first_boundary"] = quiz_params["first_boundary"]
    quiz_settings["last_boundary"] = quiz_params["last_boundary"]
    quiz_settings["tests"] = quiz_params["tests"]
    cache.set(cache_name, quiz_settings, 3600)


def edit_user_cache_form(request, slug: str, quiz_settings: dict,
        cleaned_data: dict, first_boundary: int, last_boundary: int,
        tests) -> None:
    edit_user_cache(request, slug, quiz_settings,
                {"quiz_name": cleaned_data["quiz_name"], "test_number": 
            cleaned_data["test_number"], "show_number":
            cleaned_data["show_number"],"shuffle_variant":
            cleaned_data["shuffle_variant"], "first_boundary": first_boundary, 
            "last_boundary": last_boundary, "tests": tests})