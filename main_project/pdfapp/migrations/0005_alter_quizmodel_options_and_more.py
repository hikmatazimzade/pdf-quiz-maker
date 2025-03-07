# Generated by Django 5.1.6 on 2025-03-02 13:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pdfapp", "0004_rename_quiz_model_quizmodel"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="quizmodel",
            options={"verbose_name": "Quiz", "verbose_name_plural": "Quizzes"},
        ),
        migrations.AlterField(
            model_name="quizmodel",
            name="max_test_number",
            field=models.IntegerField(default=0, verbose_name="Maximum Test Number"),
        ),
        migrations.AlterField(
            model_name="quizmodel",
            name="slug",
            field=models.SlugField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name="quizmodel",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddIndex(
            model_name="quizmodel",
            index=models.Index(fields=["slug", "user"], name="quizzes_slug_e5f34e_idx"),
        ),
        migrations.AlterModelTable(
            name="quizmodel",
            table="quizzes",
        ),
    ]
