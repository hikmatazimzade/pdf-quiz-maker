from celery import shared_task
from django.core.cache import cache
from django.utils.text import slugify
import fitz
from .models import QuizModel
from account.models import ProfileModel
import json
import base64


@shared_task
def create_quiz_task(cur_id, base64_content, variant_number, quiz_name, test_number, show_number, shuffle_variant, slider1, slider2):
    file_open = True
    try:
        file_content = base64.b64decode(base64_content.encode('utf-8'))
        doc = fitz.open(stream = file_content, filetype = "pdf")
        pdf_quiz = save_tests(doc = doc, variant_number = variant_number, slider1 = slider1, slider2 = slider2)
        doc.close()
        file_open = False


        length = len(pdf_quiz)
        serialized_data = serialize_quiz_data(pdf_quiz)


        if test_number > length:
            error_message = "There are not this many tests in this pdf!"
            cache.set(f"cre_stat_{cur_id}", {"status" : "error", "message" : error_message}, 10)
            return None



        quiz_model_instance = QuizModel(quiz_name = quiz_name, test_number = test_number, max_test_number = length, first_boundary = 1, last_boundary = length, show_number = show_number, shuffle_variant = shuffle_variant, tests = serialized_data, user_id = cur_id)
        slug = slugify(quiz_name)
        cache_name = str(cur_id) + slug
        
        
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
            "id" : cur_id
        }, 3600)
        quiz_model_instance.save()


        profile_model = ProfileModel.objects.get(user__id = cur_id)
        profile_model.current_quiz_number += 1
        profile_model.save()
        

        cache.set(f"cre_stat_{cur_id}", {"status" : "success"}, 10)
        return None
        

    except:
        if file_open:
            doc.close()

        error_message = "An error occured!"
        cache.set(f"cre_stat_{cur_id}", {"status" : "error", "message" : error_message}, 10)
        return None


def get_variants(variant_number):
    if variant_number == 4 : return ('A)', 'B)', 'C)', 'D)')
    elif variant_number == 5 : return ('A)', 'B)', 'C)', 'D)', 'E)')
    elif variant_number == 6 : return ('A)', 'B)', 'C)', 'D)', 'E)', 'F)')



def get_questions_tests(page_text, questions, tests, variants, current, last_variant, count_question, slider1, slider2) -> tuple:
    for line in page_text.split('\n'):
        line = line.strip()
        if line != '':
            if (len(line) > 2) and (line[0].isdigit() or line[1].isdigit()) and last_variant:
                if count_question - 1 == slider2 : return current, last_variant, count_question, True
                
                if count_question >= slider1:
                    questions.append(line)
                    
                current = True
                last_variant = False
                
                count_question += 1


            elif count_question >= slider1 and variants[0] in line or variants[1] in line or variants[2] in line or variants[3] in line or \
                    variants[-1] in line or variants[-2] in line:
                tests.append(line)
                if variants[-1] in line:
                    last_variant = True
                current = False


            elif count_question >= slider1:
                if current:
                    if questions: questions[-1] += line
                else:
                    if tests: tests[-1] += line

    return current, last_variant, count_question, False


def get_answers(annotations, answers, page, variants, last_rect, count_ans, slider1, slider2) -> tuple:
    for annotation in annotations:
        if annotation and annotation.type[0] == 8:
            rect = annotation.rect

            if last_rect and rect == last_rect:
                continue

            try:
                extracted_text = page.get_text("text", clip = rect).replace('\n', '')
                if variants[0] in extracted_text or variants[1] in extracted_text or variants[
                    2] in extracted_text or variants[3] in extracted_text or variants[-1] in extracted_text or \
                        variants[-2] in extracted_text:
                    if count_ans - 1 == slider2 : return last_rect, count_ans, True
                    
                    if count_ans >= slider1:
                        answers.append(extracted_text)
                    
                    
                    count_ans += 1

                else:
                    answers[-1] += extracted_text

                last_rect = rect

            except:
                pass


    return last_rect, count_ans, False


def get_dict(questions, tests, answers, variant_number, variants):
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


def save_tests(doc, variant_number, slider1, slider2):
    questions, tests, answers = [], [], []
    variants = get_variants(variant_number)

    current, last_variant = True, True
    last_rect = None
    count_question, count_ans = 1, 1
    
    for page in doc:
        page_text = page.get_text('text')
        current, last_variant, count_question, condition_question = get_questions_tests(page_text, questions, tests, variants, current,
                                                    last_variant, count_question, slider1, slider2)

        annotations = page.annots()
        annotations = sorted(annotations, key=lambda annot: annot.rect.y0 if annot.type[0] == 8 else float('inf'))

        if annotations:
            last_rect, count_ans, condition_ans = get_answers(annotations, answers, page, variants, last_rect,
                                                              count_ans, slider1, slider2)

        if condition_question and condition_ans : break

    questions, tests, answers = tuple(questions), tuple(tests), tuple(answers)

    pdf_quiz = get_dict(questions, tests, answers, variant_number, variants)
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


    '''for quiz in quiz_data:
        for tests, answer_index in quiz.items():
            key = '~ '.join(tests)
            pdf_quiz.append({key: answer_index})'''

    return json.dumps(pdf_quiz)