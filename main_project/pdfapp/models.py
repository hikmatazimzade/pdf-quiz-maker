from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class QuizModel(models.Model):
    quiz_name = models.CharField(max_length = 30)
    slug = models.SlugField(max_length = 30, default = '', blank = True, db_index = True)
    test_number = models.IntegerField(default = 0)
    max_test_number = models.IntegerField(default = 0)
    first_boundary = models.IntegerField(default = 0)
    last_boundary = models.IntegerField(default = 1)
    show_number = models.BooleanField(default = False)
    shuffle_variant = models.BooleanField(default = False)
    
    tests = models.TextField(max_length = 300000)
    user = models.ForeignKey(User, on_delete = models.CASCADE, default = '', db_index = True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.quiz_name)
        super(QuizModel, self).save(*args, **kwargs)


    def __str__ (self):
        return self.quiz_name