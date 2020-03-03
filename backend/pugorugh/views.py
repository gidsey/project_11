from django.contrib.auth import get_user_model
from django.http import Http404
from django.db.models import Q

from rest_framework import permissions, status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    RetrieveAPIView
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

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

        age = user_prefs.age.split(',')

        if age[0] == 'b':
            age_lower = 0
            age_upper = 10
        if age[0] == 'y':
            age_lower = 11
            age_upper = 20
        if age[0] == 'a':
            age_lower = 21
            age_upper = 89
        if age[0] == 's':
            age_lower = 90
            age_upper = 200  # This approach needs work / re-thinking.

        age_lower = 0
        age_upper = 200

        print('Age: {}'.format(age))

        matched_dogs = models.Dog.objects.all().filter(
            Q(gender__in=user_prefs.gender.split(',')) &
            Q(size__in=user_prefs.size.split(',')) &
            Q(age__gt=age_lower) &
            Q(age__lte=age_upper)
        )

        print('There are {} matched dogs'.format(len(matched_dogs)))

        liked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='l'))]

        disliked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='d'))]

        appraised_dogs = liked_dogs + disliked_dogs
        undecided_dogs = [dog for dog in matched_dogs if dog not in appraised_dogs]  # Return only undecided dogs

        liked_dogs.sort(key=lambda x: x.id)
        disliked_dogs.sort(key=lambda x: x.id)
        undecided_dogs.sort(key=lambda x: x.id)  # Sort each list by ID

        print()
        print('undecided_dogs {}'.format(undecided_dogs))
        print('liked_dogs {}'.format(liked_dogs))
        print('disliked_dogs {}'.format(disliked_dogs))
        print()

        if current_status == 'l':
            pick_list = [dog for dog in liked_dogs if dog.id > pk]  # Filtered list of liked_dogs
        if current_status == 'd':
            pick_list = [dog for dog in disliked_dogs if dog.id > pk]  # Filtered list of disliked_dogs
        if current_status == 'u':
            pick_list = [dog for dog in undecided_dogs if dog.id > pk]  # Filtered list of undecided

        print('pick_list {}'.format(pick_list))

        try:
            dog = pick_list[0]  # Show the next dog
            return dog
        except IndexError:

            if current_status == 'l':
                if liked_dogs:
                    return liked_dogs[0]  # Loop back around to 1st liked dog
                else:
                    return Http404 # There are no results to show

            if current_status == 'd':
                if disliked_dogs:
                    return disliked_dogs[0]  # Loop back around to 1st disliked dog
                else:
                    return Response(status=current_status.HTTP_404_NOT_FOUND) # There are no results to show

            if current_status == 'u':
                if undecided_dogs:
                    return undecided_dogs[0]  # Loop back around to 1st undecided dog
                else:
                    return Http404 # There are no results to show

