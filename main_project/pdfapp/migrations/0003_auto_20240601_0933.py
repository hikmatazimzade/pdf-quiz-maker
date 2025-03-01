from django.db import migrations, models
from django.contrib.auth.models import User
import django
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pdfapp', '0002_quiz_model_shuffle_variant'),
    ]

    operations = [
        migrations.AlterField(
            model_name = 'Quiz_Model',
            name = 'slug',
            field = models.SlugField(max_length = 30, default = '', blank = True, db_index = True),
        ),
        
        migrations.AlterField(
            model_name = 'Quiz_Model',
            name = 'tests',
            field = models.TextField(max_length = 300000),
        ),
        
        migrations.AlterField(
            model_name = 'Quiz_Model',
            name = 'user',
            field = models.ForeignKey(default='', on_delete = django.db.models.deletion.CASCADE, to = settings.AUTH_USER_MODEL),
        ),
    ]