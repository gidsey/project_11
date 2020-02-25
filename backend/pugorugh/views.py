from django.contrib.auth import get_user_model

from rest_framework import permissions
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    RetrieveAPIView
)
from rest_framework.mixins import CreateModelMixin

from . import serializers
from . import models

from django.db.models import Q


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


class UserDogStatus(CreateModelMixin, RetrieveUpdateAPIView):
    """
    Set User-Dog Status (l)iked or (d)isliked.
    Endpoints: /api/dog/<pk>/liked/ or /api/dog/<pk>/disliked/
    Method: PUT

    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        dog_id = self.kwargs['pk']
        try:
            user_dog = models.UserDog.objects.get(user=self.request.user.id, dog_id=dog_id)
        except models.UserDog.DoesNotExist:
            user_dog = models.UserDog.objects.create(user=self.request.user, dog_id=dog_id, status='l')
        return user_dog


class Dogs(RetrieveAPIView):
    """
    Get next undecided dog.
    Endpoint: /api/dog/<pk>/undecided/next/
    Method: GET
    """
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        pk = self.kwargs['pk']  # Initially set to -1
        # all_the_dogs = self.get_queryset()  # Get all the dogs
        # print('all_the_dogs: {}'.format(all_the_dogs))

        liked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
                Q(user__exact=self.request.user.id) &
                Q(status__exact='l'))]

        print('pk: {}'.format(pk))
        print('liked_dogs: {}'.format(liked_dogs))
        liked_dogs.sort(key=lambda x: x.id)

        pick_list = []
        for dog in liked_dogs:
            if dog.id > int(pk):
                pick_list.append(dog)
        print('pick_list {}'.format(pick_list))
        # pick_list.sort(key=lambda x: x.id)
        print('pick_list {}'.format(pick_list))
        try:
            dog = pick_list[0]
            return dog
        except IndexError:
            return liked_dogs[0]


        #


        # if int(pk) == -1:
        #         #     return liked_dogs[0]
        # else:
        #     return liked_dogs[int(liked_dogs.index) + 1]


        # for dog in liked_dogs:
        #     if dog.id > int(pk):

        #
        # disliked_dogs = self.get_queryset()

        # print('There are {} liked_dogs.'.format(len(liked_dogs)))
        # print('liked_dogs: {}'.format(liked_dogs))

        # return liked_dogs[1]


        # dog = liked_dogs.filter(id__gt=pk).first()  # Retrieve the dog with the next highest id
        # pos = liked_dogs.index > pk
        # liked_dogs = iter(liked_dogs)


        #
        # for dog in liked_dogs:
        #     if dog.id > int(pk):
        #         unseen_liked_dogs.append(dog)
        #
        # print('unseen_liked_dogs {}'.format(unseen_liked_dogs))
        #
        # return unseen_liked_dogs[0]



        # # dog = next(iter(liked_dogs))
        # if dog is not None:
        #     return dog
        # else:
        #     return liked_dogs[0]
        #     # return liked_dogs.first()  # Loop back around
