from operator import attrgetter
from itertools import chain

from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import permissions
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    RetrieveAPIView
)
from rest_framework.exceptions import NotFound
from rest_framework.mixins import CreateModelMixin

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    """
    Register Users.
    """
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class UserPrefs(CreateModelMixin, RetrieveUpdateAPIView):
    """
    List or Create User Preferences.
    Endpoint: /api/user/preferences
    Methods: GET and PUT
    """
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        try:
            #  Get the UserPrefs object for the current user if it exists
            user_prefs = models.UserPref.objects.get(user=self.request.user.id)
        except models.UserPref.DoesNotExist:
            #  Else create a UserPrefs object for the current user
            user_prefs = models.UserPref.objects.create(user=self.request.user)
        return user_prefs

    def perform_update(self, serializer):
        serializer.save()


class SetStatus(CreateModelMixin, RetrieveUpdateAPIView):
    """
    Set User-Dog Status (l)iked or (d)isliked.
    Endpoints: /api/dog/<pk>/liked/ or /api/dog/<pk>/disliked/
    Method(s): PUT

    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        dog_id = self.kwargs['pk']
        new_status = self.kwargs['status'][0]  # returns l, d or u
        try:
            user_dog = models.UserDog.objects.get(user=self.request.user.id, dog_id=dog_id)
            user_dog.status = new_status
            user_dog.save()
        except models.UserDog.DoesNotExist:
            user_dog = models.UserDog.objects.create(user=self.request.user, dog_id=dog_id, status=new_status)
        return user_dog


class Dogs(RetrieveAPIView):
    """
    Get next undecided / liked / disliked dog.
    Endpoints:
            /api/dog/<pk>/undecided/next/
            /api/dog/<pk>/liked/next/
            /api/dog/<pk>/disliked/next/
    Method(s): GET
    """
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        current_status = self.kwargs['status'][0]  # returns l, d or u

        if current_status == 'u':  # undecided dogs
            user_prefs = models.UserPref.objects.all().get(user=self.request.user)
            age_prefs = user_prefs.age.split(',')
            b_lower = b_upper = y_lower = y_upper = a_lower = a_upper = s_lower = s_upper = -1

            if 'b' in age_prefs:
                b_lower = 0
                b_upper = 10
            if 'y' in age_prefs:
                y_lower = 11
                y_upper = 20
            if 'a' in age_prefs:
                a_lower = 21
                a_upper = 70
            if 's' in age_prefs:
                s_lower = 71
                s_upper = 200  # Set the age ranges

            matched_dogs = models.Dog.objects.all().filter(
                Q(gender__in=user_prefs.gender.split(',')) &
                Q(size__in=user_prefs.size.split(',')))

            matched_dogs = matched_dogs.filter(
                Q(age__range=(b_lower, b_upper)) |
                Q(age__range=(y_lower, y_upper)) |
                Q(age__range=(a_lower, a_upper)) |
                Q(age__range=(s_lower, s_upper))
            )
            print('{} matched_dogs'.format(len(matched_dogs)))

            unrated_dogs = matched_dogs.exclude(
                dog_user__user_id__exact=self.request.user.id
                )   # Include all dogs that have yet to be rated

            print('{} 1st filter unrated_dogs'.format(len(unrated_dogs)))

            u_dogs = matched_dogs.filter(
                Q(dog_user__user_id__exact=self.request.user.id) &
                Q(dog_user__status__exact='u')
                )   # Include all dogs explicitly rated as 'undecided'

            print('{} 2nd filter u_dogs'.format(len(u_dogs)))

            undecided_dogs = (unrated_dogs | u_dogs).distinct()


            print('{} undecided_dogs'.format(len(undecided_dogs)))
            print('undecided_dogs: {}'.format(undecided_dogs))

            if not undecided_dogs:
                raise NotFound  # No matching dogs so raise 404
            else:
                print('{} undecided_dogs'.format(len(undecided_dogs)))
                return undecided_dogs

        if current_status == 'l' or current_status == 'd':  # liked or disliked dogs
            chosen_dogs = models.Dog.objects.all().filter(
                Q(dog_user__user_id__exact=self.request.user.id) &
                Q(dog_user__status__exact=current_status))
            if not chosen_dogs:
                raise NotFound
            else:
                print('{} chosen_dogs'.format(len(chosen_dogs)))
                return chosen_dogs

    def get_object(self):
        pk = int(self.kwargs['pk'])  # Initially set to -1
        dog = self.get_queryset().filter(id__gt=pk).first()  # Retrieve the dog with the next highest id
        if dog is not None:
            return dog
        else:
            return self.get_queryset().first()  # Loop back around
