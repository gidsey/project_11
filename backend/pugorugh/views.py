from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import permissions
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    RetrieveAPIView,
    DestroyAPIView)
from rest_framework.exceptions import NotFound
from rest_framework.mixins import CreateModelMixin

from . import serializers
from . import models
from .utils import get_age_range, get_microchipped


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
    Endpoint: /api/user/preferences/
    Methods: GET, PUT, PATCH
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
    Set User-Dog Status to liked, disliked or undecided.
    Endpoints:
        /api/dog/<pk>/liked/
        /api/dog/<pk>/disliked/
        /api/dog/<pk>/undecided/
    Methods: GET, PUT, PATCH

    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        dog_id = self.kwargs['pk']
        new_status = self.kwargs['status'][0]  # returns l, d, u or b (liked, disliked or undecided)
        try:
            user_dog = models.UserDog.objects.get(user=self.request.user.id, dog_id=dog_id)
            user_dog.status = new_status
            user_dog.save()
        except models.UserDog.DoesNotExist:
            user_dog = models.UserDog.objects.create(
                user=self.request.user,
                dog_id=dog_id,
                status=new_status
            )
        return user_dog


class Blacklist(CreateModelMixin, RetrieveUpdateAPIView):
    """
    Set User-Dog blacklist to be either True or False
    Endpoints:
        /api/dog/<pk>/blacklist/true/
        /api/dog<pk>/blacklist/false/
    Methods: GET, PUT, PATCH
    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        dog_id = self.kwargs['pk']
        blacklist = self.kwargs['blacklist']  # returns True or False
        try:
            user_dog = models.UserDog.objects.get(user=self.request.user.id, dog_id=dog_id)
            user_dog.blacklist = blacklist
            user_dog.save()
        except models.UserDog.DoesNotExist:
            user_dog = models.UserDog.objects.create(
                user=self.request.user,
                dog_id=dog_id,
                blacklist=blacklist,
                status='u',
            )
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

        # undecided dogs
        if current_status == 'u':
            user_prefs = models.UserPref.objects.all().get(user=self.request.user)
            age = user_prefs.age.split(',')  # returns a combination of 'b,y,a,s'

            # Use the utils helper functions
            age_ranges = get_age_range(age)
            microchipped = get_microchipped(user_prefs.microchipped)

            #  Filer by Microchipped (no_preference, yes or no)
            if microchipped == 'no_preference':
                chipped_dogs = models.Dog.objects.all()
            else:
                chipped_dogs = models.Dog.objects.all().filter(
                    microchipped__exact=microchipped)

            # Filter by Gender, Size and Age Range
            matched_dogs = chipped_dogs.filter(
                Q(gender__in=user_prefs.gender.split(',')) &
                Q(size__in=user_prefs.size.split(',')) &
                Q(age__in=age_ranges)
            )

            # Get all dogs that have yet to be rated
            unrated_dogs = matched_dogs.exclude(
                dog_user__user_id__exact=self.request.user.id
            )

            # Get all dogs explicitly rated as 'undecided'
            rated_dogs = matched_dogs.filter(
                Q(dog_user__user_id__exact=self.request.user.id) &
                Q(dog_user__status__exact='u') &
                Q(dog_user__blacklist__exact=False)
            )

            # Combine querysets & remove duplicates
            undecided_dogs = (unrated_dogs | rated_dogs).distinct()

            if not undecided_dogs:
                raise NotFound  # No matching dogs so raise 404
            else:
                return undecided_dogs

        # liked or disliked dogs
        if current_status == 'l' or current_status == 'd':
            chosen_dogs = models.Dog.objects.all().filter(
                Q(dog_user__user_id__exact=self.request.user.id) &
                Q(dog_user__status__exact=current_status) &
                Q(dog_user__blacklist__exact=False))

            if not chosen_dogs:
                raise NotFound
            else:
                return chosen_dogs

    def get_object(self):
        pk = int(self.kwargs['pk'])  # Initially set to -1

        # Retrieve the dog with the next highest id
        dog = self.get_queryset().filter(id__gt=pk).first()
        if dog is not None:
            return dog
        else:
            return self.get_queryset().first()  # Loop back around


class AddDog(CreateAPIView):
    """
    Provide a method that allows a
    Dog instance to be added to the DB.
    Endpoints:
            /api/dog/add/
    Method(s): POST
    """
    serializer_class = serializers.DogSerializer

    def perform_create(self, serializer):
        serializer.save()


class DeleteDog(DestroyAPIView):
    """
    Provide a method that allows a
    Dog instance to be deleted from the DB.
    Endpoints:
            /api/dog/<pk>/delete/
    Method(s): DELETE
    """
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def perform_destroy(self, instance):
        instance.delete()
