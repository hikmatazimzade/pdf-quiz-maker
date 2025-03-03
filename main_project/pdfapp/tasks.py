from typing import List, Optional
import json
import base64
import logging

from django.core.cache import cache
from django.utils.text import slugify
from celery import shared_task
import fitz

from account.models import ProfileModel
from pdfapp.models import QuizModel

logger = logging.getLogger(__name__)


@shared_task
def create_quiz_task(curr_id: int, base64_content: base64,
        variant_number: int,quiz_name: str, test_number: int,
        show_number: bool, shuffle_variant: bool, slider1: int, slider2: int):
    file_open = True
    try:
        file_content = base64.b64decode(base64_content.encode('utf-8'))
        doc = fitz.open(stream=file_content, filetype="pdf")
        pdf_quiz = save_tests(doc=doc, variant_number=variant_number,
                            slider1=slider1, slider2=slider2)
        
        doc.close()
        file_open = False

        length = len(pdf_quiz)
        serialized_data = serialize_quiz_data(pdf_quiz)

        if test_number > length:
            error_message = "There are not this many tests in this pdf!"
            cache.set(f"cre_stat_{curr_id}", {"status" : "error", "message" : error_message}, 10)
            return None

        quiz_model_instance = QuizModel(quiz_name=quiz_name, test_number=test_number,
                        max_test_number=length, first_boundary=1,
                        last_boundary=length, show_number=show_number,
                        shuffle_variant=shuffle_variant,
                        tests=serialized_data, user_id=curr_id)
        
        slug = slugify(quiz_name)
        cache_name = str(curr_id) + slug
        
        cache.set(cache_name, {
            "slug" : slug,
            "quiz_name" : quiz_name,
            "test_number" : test_number,
            "max_test_number" : length,
            "first_boundary" : 1,
            "last_boundary" : length,
            "show_number" : show_number,
            "shuffle_variant" : shuffle_variant,
            "tests" : serialized_data,
            "id" : curr_id
        }, 3600)
        quiz_model_instance.save()

        profile_model = ProfileModel.objects.get(user__id=curr_id)
        profile_model.current_quiz_number += 1
        profile_model.save()
        
        cache.set(f"cre_stat_{curr_id}", {"status" : "success"}, 10)
        return None
    
    except Exception as quiz_celery_error:
        logger.error(f"Quiz Create Celery Error -> {quiz_celery_error}")
        if file_open:
            doc.close()

        error_message = "An error occured!"
        cache.set(f"cre_stat_{curr_id}", {"status" : "error", "message" : error_message}, 10)
        return None


def get_variants(variant_number: int)-> tuple:
    if variant_number == 4:
        return ('A)', 'B)', 'C)', 'D)')
    elif variant_number == 5:
        return ('A)', 'B)', 'C)', 'D)', 'E)')
    else:
        return ('A)', 'B)', 'C)', 'D)', 'E)', 'F)')


def get_questions_tests(page_text: fitz, 
            questions: List[str], tests: List[str],
            variants: List[str], current,last_variant: bool) -> tuple:
    for line in page_text.split('\n'):
        line = line.strip()
        if line != '':
            if (len(line) >= 2) and (line[0].isdigit() or \
                                     line[1].isdigit()) and last_variant:
                questions.append(line)    
                current = True
                last_variant = False

            elif any(
                variant in line
                for variant in (variants[0], variants[1],
                    variants[2], variants[3], variants[-1], variants[-2])
                    ):
                tests.append(line)
                if variants[-1] in line:
                    last_variant = True
                current = False

            else:
                if current:
                    if questions: questions[-1] += line
                else:
                    if tests: tests[-1] += line

    return current, last_variant


def get_answers(annotations: fitz, answers: List[str], page: fitz,
    variants: List[str], last_rect: Optional[fitz.open]) -> tuple:
    for annotation in annotations:
        if annotation and annotation.type[0] == 8:
            rect = annotation.rect

            if last_rect and rect == last_rect:
                continue

            try:
                extracted_text = page.get_text("text", clip=rect). \
                        replace('\n', '')
                if variants[0] in extracted_text or variants[1] in \
                extracted_text or variants[2] in extracted_text or \
                variants[3] in extracted_text or variants[-1] in \
                extracted_text or variants[-2] in extracted_text:
                    answers.append(extracted_text)

                else:
                    answers[-1] += extracted_text

                last_rect = rect

            except:
                pass


    return last_rect


def get_dict(questions: List[str], tests: List[str], answers: List[str],
variant_number: List[str], variants: List[str]) -> List[dict]:
    pdf_quiz = []

    for i in range((len(answers))):
        current_i = i * variant_number
        current_question = questions[i]
        current_tests = tests[current_i: current_i + variant_number]
        current_answer = answers[i].replace(' ', '')
        current_number = 0

        for l in range(len(variants)):
            if variants[l] in current_answer:
                current_number = l
                break

        pdf_quiz.append({
            'question': current_question,
            'answers': current_tests,
            'correctAnswer': current_number
        })

    return pdf_quiz


def save_tests(doc: fitz.open, variant_number: int,
               slider1: int, slider2: int) -> List[dict]:
    questions, tests, answers = [], [], []
    variants = get_variants(variant_number)

    current, last_variant = True, True
    last_rect = None
    
    for page in doc:
        page_text = page.get_text('text')
        current, last_variant = get_questions_tests(page_text, questions,
        tests, variants, current, last_variant)

        annotations = page.annots()
        annotations = sorted(annotations, key=lambda annot: annot.rect.y0 \
        if annot.type[0] == 8 else float('inf'))

        if annotations:
            last_rect = get_answers(annotations, answers, page, variants, last_rect)

    questions, tests, answers = tuple(questions), tuple(tests), tuple(answers)

    pdf_quiz = get_dict(questions, tests, answers, variant_number, \
    variants)[slider1 - 1:slider2 - 1]
    return pdf_quiz


def serialize_quiz_data(quiz_data):
    pdf_quiz = []

    for quiz in quiz_data:
        answers = '~ '.join(quiz.get('answers'))
        
        pdf_quiz.append({
            'question' : quiz.get('question', ''),
            'answers' : answers,
            'correctAnswer' : quiz.get('correctAnswer', '')
        })

    return json.dumps(pdf_quiz)