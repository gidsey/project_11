from django.contrib.auth.models import User
from django.db import models


class Dog(models.Model):
    """
    This model represents a dog in the app.
    """
    name = models.CharField(max_length=255)
    image_filename = models.CharField(max_length=255)
    breed = models.CharField(max_length=255, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=1)
    size = models.CharField(max_length=2)
    microchipped = models.BooleanField(default=False)

    def __str__(self):
        return '{}, {} ({})'.format(self.id, self.name, self.gender)


class UserDog(models.Model):
    """
     This model represents a link between a user an a dog.
    """
    user = models.ForeignKey(User, related_name='user_dog', on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, related_name='dog_user', on_delete=models.CASCADE)
    status = models.CharField(max_length=1)


class UserPref(models.Model):
    """
    This model contains the user's preferences.
    """
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    age = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    microchipped = models.CharField(max_length=255, default='u')




