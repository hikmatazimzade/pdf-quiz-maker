# Generated by Django 5.1.6 on 2025-03-02 13:20

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Profile_Model",
            new_name="ProfileModel",
        ),
    ]
