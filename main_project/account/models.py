from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, null = False)
    current_quiz_number = models.IntegerField(default = 0)
    avatar = models.ImageField(upload_to = 'account', blank = True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile_model.save()
        
    except ProfileModel.DoesNotExist:
        ProfileModel.objects.create(user=instance)