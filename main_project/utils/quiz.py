from typing import List, Optional
from random import shuffle
import logging
import json

from django.core.cache import cache
from django.shortcuts import render

from pdfapp.models import Quiz_Model
from pdfapp.forms import Edit_Quiz_Form

logger = logging.getLogger(__name__)


def get_quiz_settings(request, slug, *keys: tuple):
    cache_name = str(request.user.id) + slug
    cached_data = cache.get(cache_name)

    if cached_data:
        return {key: cached_data[key] for key in keys}

    else:
        try:
            user_quiz = Quiz_Model.objects.get(user = request.user, slug = slug)
            return {key: getattr(user_quiz, key, None) for key in keys}

        except Exception as quiz_error:
            logger.error(
                f"Error Occurred While Getting Quiz From Db -> {quiz_error}")
            return None


def fetch_edit_quiz_settings(request, slug) -> Optional[dict]:
    return get_quiz_settings(request, slug, "first_boundary",
        "last_boundary", "quiz_name", "test_number", "show_number",
        "shuffle_variant", "max_test_number")


def fetch_quiz_settings(request, slug) -> Optional[dict]:
    return get_quiz_settings(request, slug, "tests","first_boundary",
        "last_boundary", "test_number","shuffle_variant", "show_number")


def initialize_edit_form(quiz_settings: dict) -> Edit_Quiz_Form:
    return Edit_Quiz_Form(initial = {
            'quiz_name' : quiz_settings["quiz_name"],
            'test_number' : quiz_settings["test_number"],
            'show_number' : quiz_settings["show_number"],
            'shuffle_variant' : quiz_settings["shuffle_variant"]
        })

def render_quiz_edit_page(request, form, quiz_settings, slug):
    total_range = quiz_settings["last_boundary"] - \
    quiz_settings["first_boundary"]
    return render(request, 'pdfapp/edit_quiz.html', {
        'form' : form,
        'slug' : slug,
        'total_range' : total_range,
        'max_test_number' : quiz_settings["max_test_number"],
        'first_boundary' : quiz_settings["first_boundary"],
        'last_boundary' : quiz_settings["last_boundary"]
    })

def process_edit_form(request, quiz_settings: dict) -> Edit_Quiz_Form:
    return Edit_Quiz_Form(request.POST or None, request = request,
            max_test_number = quiz_settings["max_test_number"], initial = {
            'quiz_name' : quiz_settings["quiz_name"],
        })


def get_quiz_data(quiz_data_json: str, first_boundary: int,
                  last_boundary: int) -> List[dict]:
    quiz_tests = json.loads(quiz_data_json)
    quiz_data = []

    for quiz_item in quiz_tests:
            answers = quiz_item.get('answers').split('~ ')
            quiz_data.append({
                'question' : quiz_item.get('question', ''),
                'answers' : answers,
                'correctAnswer' : quiz_item.get('correctAnswer', '')
            })
        
    
    quiz_data = quiz_data[first_boundary - 1 : last_boundary]
    return quiz_data


def shuffle_answers(answers: List[str], variants: tuple, correct_answer: int) -> int:
    answer_number = len(answers)
    for num in range(answer_number):
        answers[num] = answers[num].replace(variants[num], '')

    correct_answer = answers[correct_answer]
    shuffle(answers)
    new_correct_answer = 0

    for num in range(answer_number):
        if answers[num] == correct_answer:
            new_correct_answer = num
            break

    for n in range(len(answers)):
        answers[n] = variants[n] + answers[n]
    return new_correct_answer


def shuffle_quiz_data(quiz_data: List[dict], test_number: int) -> None:
    shuffle(quiz_data)
    quiz_data = quiz_data[:test_number]

    variant_number = len(quiz_data[0]['answers'])
    variants_dict = {
        4: ('A)', 'B)', 'C)', 'D)'),
        5: ('A)', 'B)', 'C)', 'D)', 'E)'),
        6: ('A)', 'B)', 'C)', 'D)', 'E)', 'F)')
    }

    variants = variants_dict[variant_number]
    quiz_data_length = len(quiz_data)

    for i in range(quiz_data_length):
        answers = quiz_data[i]['answers']
        new_correct_answer = shuffle_answers(answers, variants, quiz_data[i]['correctAnswer'])

        quiz_data[i]['answers'] = answers
        quiz_data[i]['correctAnswer'] = new_correct_answer