from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class QuizModel(models.Model):
    quiz_name = models.CharField(max_length=30, null=False)
    slug = models.SlugField(max_length=30, null=False, unique=True)
    test_number = models.IntegerField(default=0)
    max_test_number = models.IntegerField(default=0,
                                          verbose_name="Maximum Test Number")
    first_boundary = models.IntegerField(default=0)
    last_boundary = models.IntegerField(default=1)
    show_number = models.BooleanField(default=False)
    shuffle_variant = models.BooleanField(default=False)
    tests = models.TextField(max_length=300_000)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    
    class Meta:
        indexes = [
            models.Index(fields=["slug", "user"])
        ]
        db_table = "quizzes"

        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.quiz_name)
        super(QuizModel, self).save(*args, **kwargs)

    def __str__ (self):
        return self.quiz_name