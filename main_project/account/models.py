from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_quiz_number = models.IntegerField(default=0,
                                        verbose_name="Current Quiz Number")
    avatar = models.ImageField(upload_to='account', blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profilemodel.save()
    
    except ProfileModel.DoesNotExist:
        ProfileModel.objects.create(user=instance)