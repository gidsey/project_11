from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q

from rest_framework import permissions
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    RetrieveAPIView
)
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
    Method: PUT

    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        dog_id = self.kwargs['pk']
        status = self.kwargs['status'][0]  # returns l, d or u
        print('setstatus={}'.format(status))
        try:
            user_dog = models.UserDog.objects.get(user=self.request.user.id, dog_id=dog_id, status=status)
            print(user_dog.status)

        except models.UserDog.DoesNotExist:
            user_dog = models.UserDog.objects.create(user=self.request.user, dog_id=dog_id, status=status)
        return user_dog


class Dogs(RetrieveAPIView):
            """
            Get next liked/disliked/undecided dog.
            Endpoints:
                /api/dog/<pk>/liked/next/
                /api/dog/<pk>/disliked/next/
                /api/dog/<pk>/undecided/next/
            Method: GET
            """
            queryset = models.UserDog.objects.all()
            serializer_class = serializers.DogSerializer

            def get_object(self):
                pk = int(self.kwargs['pk'])  # Initially set to -1
                status = self.kwargs['status'][0]  # returns l, d or u

                liked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
                    Q(user__exact=self.request.user.id) &
                    Q(status__exact='l'))]

                disliked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
                    Q(user__exact=self.request.user.id) &
                    Q(status__exact='d'))]

                all_the_dogs = models.Dog.objects.all()  # Get all the dogs
                undecided_dogs = [dog for dog in all_the_dogs if dog not in liked_dogs or dog not in disliked_dogs]

                liked_dogs.sort(key=lambda x: x.id)
                disliked_dogs.sort(key=lambda x: x.id)
                undecided_dogs.sort(key=lambda x: x.id)  # Sort each list by ID

                print('liked_dogs {}'.format(liked_dogs))
                print('disliked_dogs {}'.format(disliked_dogs))
                print('undecided_dogs {}'.format(undecided_dogs))
                print('status={}'.format(status))
                if status == 'l':
                    pick_list = [dog for dog in liked_dogs if dog.id > pk]  # Filtered list of liked_dogs
                if status == 'd':
                    pick_list = [dog for dog in disliked_dogs if dog.id > pk]  # Filtered list of disliked_dogs
                if status == 'u':
                    pick_list = [dog for dog in undecided_dogs if dog.id > pk]  # Filtered list of undecided

                print('pick_list {}'.format(pick_list))

                try:
                    dog = pick_list[0]  # Show the next dog
                    return dog
                except IndexError:
                    if status == 'l':
                        return liked_dogs[0]  # Loop back around
                    if status == 'd':
                        return disliked_dogs[0]  # Loop back around
                    if status == 'u':
                        return undecided_dogs[0]  # Loop back around


