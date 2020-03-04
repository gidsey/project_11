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
    Get next liked/disliked/undecided dog.
    Endpoints:
            /api/dog/<pk>/liked/next/
            /api/dog/<pk>/disliked/next/
            /api/dog/<pk>/undecided/next/
    Method(s): GET
    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        pk = int(self.kwargs['pk'])  # Initially set to -1
        current_status = self.kwargs['status'][0]  # returns l, d or u
        user_prefs = models.UserPref.objects.all().get(user=self.request.user)
        pick_list = []
        age_prefs = user_prefs.age.split(',')
        gender_prefs = user_prefs.gender.split(',')
        size_prefs = user_prefs.size.split(',')
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
            Q(gender__in=gender_prefs) &
            Q(size__in=size_prefs))

        matched_dogs = matched_dogs.filter(
            Q(age__range=(b_lower, b_upper)) |
            Q(age__range=(y_lower, y_upper)) |
            Q(age__range=(a_lower, a_upper)) |
            Q(age__range=(s_lower, s_upper))
              )

        print('There are {} matched dogs'.format(len(matched_dogs)))

        liked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='l'))]
        liked_dogs.sort(key=lambda x: x.id)

        disliked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='d'))]
        disliked_dogs.sort(key=lambda x: x.id)

        appraised_dogs = liked_dogs + disliked_dogs
        undecided_dogs = [dog for dog in matched_dogs if dog not in appraised_dogs]  # Return only undecided dogs
        undecided_dogs.sort(key=lambda x: x.id)  # Sort each list by ID

        print('There are {} undecided dogs'.format(len(undecided_dogs)))

        if current_status == 'l':
            pick_list = [dog for dog in liked_dogs if dog.id > pk]  # Filtered list of liked_dogs

        if current_status == 'd':
            pick_list = [dog for dog in disliked_dogs if dog.id > pk]  # Filtered list of disliked_dogs

        if current_status == 'u':
            pick_list = [dog for dog in undecided_dogs if dog.id > pk]  # Filtered list of undecided

        try:
            dog = pick_list[0]  # Show the next dog
            return dog
        except IndexError:

            if current_status == 'l':
                try:
                    return liked_dogs[0]  # Loop back around to 1st liked dog
                except IndexError:
                    raise NotFound  # There are no liked dogs to show

            if current_status == 'd':
                try:
                    return disliked_dogs[0]  # Loop back around to 1st disliked dog
                except IndexError:
                    raise NotFound  # There are no disliked dogs to show

            if current_status == 'u':
                try:
                    return undecided_dogs[0]  # Loop back around to 1st undecided dog
                except IndexError:
                    raise NotFound  # There are no undecided dogs to show
