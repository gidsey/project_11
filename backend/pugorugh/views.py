from django.contrib.auth import get_user_model

from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
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


class UserDogStatus(CreateModelMixin, RetrieveUpdateAPIView):
    """

    """




class Dogs(generics.RetrieveAPIView):
    """
    Get next undecided dog.
    Endpoint: /api/dog/<pk>/undecided/next/
    Method: GET
    """
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        pk = self.kwargs['pk']  # Initially set to -1
        all_the_dogs = self.get_queryset()  # Get all the dogs
        print('all_the_dogs: {}'.format(all_the_dogs))

        dog = all_the_dogs.filter(id__gt=pk).first()  # Retrieve the dog with the next highest id
        if dog is not None:
            return dog
        else:
            return all_the_dogs.first()  # Loop back around



