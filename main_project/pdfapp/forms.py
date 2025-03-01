from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import widgets
from .models import Quiz_Model
from django.utils.translation import gettext_lazy as _

class Contact_Form(forms.Form):
    name = forms.CharField(widget = widgets.TextInput(attrs = {
        'id' : 'name'
    }))


    email = forms.EmailField(widget = widgets.EmailInput(attrs = {
        'id' : 'email'
    }))


    subject = forms.CharField(validators = [MinLengthValidator(5, _('The minimum length of subject must be 5!'))], widget = widgets.TextInput(attrs = {
        'id' : 'subject'
    }))


    message = forms.CharField(max_length = 1500, validators = [MinLengthValidator(30, _('The minimum length of message must be 30!')), MaxLengthValidator(1500, 'The maximum length of message must be 1500')],widget = widgets.Textarea(attrs = {
        'id' : 'message'
    }))


class Quiz_Form(forms.Form):
    pdf = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(Quiz_Form, self).__init__(*args, **kwargs)

    quiz_name = forms.CharField(validators = [MaxLengthValidator(30)], max_length = 30, widget = widgets.TextInput(attrs = {
        'id' : 'quizName',
        "class" : "quiz_class"
    }))


    test_number = forms.IntegerField(max_value = 500, widget = widgets.NumberInput(attrs = {
        'id' : 'testNumber',
        "class" : "quiz_class"
    }))


    variant_number = forms.IntegerField(max_value = 6, widget = widgets.NumberInput(attrs = {
        'id' : 'variantNumber',
        'min' : 0,
        "class" : "quiz_class"
    }))


    show_number = forms.BooleanField(initial = False, required = False, widget = forms.CheckboxInput(attrs = {
        'class' : 'custom-toggle',
        'id' : 'showNumber'
    }))



    shuffle_variant = forms.BooleanField(initial = False, required = False, widget = forms.CheckboxInput(attrs = {
        'class' : 'custom-toggle',
        'id' : 'shuffleVariant'
    }))



    def clean_quiz_name(self):
        quiz_name = self.cleaned_data.get('quiz_name', '')
        if self.request:
            if Quiz_Model.objects.filter(quiz_name = quiz_name, user = self.request.user).exists():
                self.add_error('quiz_name', _('The pdf with this name already exists!'))

        return quiz_name


class Edit_Quiz_Form(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.max_test_number = kwargs.pop("max_test_number", 1)
        super(Edit_Quiz_Form, self).__init__(*args, **kwargs)
        

    quiz_name = forms.CharField(validators = [MaxLengthValidator(60)], max_length = 60, widget = widgets.TextInput(attrs = {
        'id' : 'quizName'
    }))


    test_number = forms.IntegerField(max_value = 1000, widget = widgets.NumberInput(attrs = {
        'id' : 'testNumber'
    }))


    show_number = forms.BooleanField(required = False, widget = forms.CheckboxInput(attrs = {
        'class' : 'custom-toggle',
        'id' : 'showNumber'
    }))


    shuffle_variant = forms.BooleanField(required = False, widget = forms.CheckboxInput(attrs = {
        'class' : 'custom-toggle',
        'id' : 'shuffleVariant'
    }))


    def clean_quiz_name(self):
        quiz_name = self.cleaned_data.get('quiz_name', '')
        initial_quiz_name = self.initial.get('quiz_name', '')
        if self.request:
            try:
                if initial_quiz_name != quiz_name and Quiz_Model.objects.filter(quiz_name = quiz_name, user = self.request.user).exists():
                    self.add_error('quiz_name', _('The pdf with this name already exists!'))
            except:
                pass

        return quiz_name
    

    def clean_test_number(self):
        test_number = self.cleaned_data.get('test_number', 1)
        if test_number > self.max_test_number:
            self.add_error('test_number', _('There are not this many tests in this pdf!'))

        try:
            slider1 = int(self.request.POST.get('slider1', 0))
            slider2 = int(self.request.POST.get('slider2', 1))
            if test_number > slider2 - slider1 + 1:
                self.add_error('test_number', _('There are not this many tests in this range!'))
        
        except:
            pass

        return test_number