from django.contrib.auth import get_user_model

from rest_framework import permissions
from rest_framework import generics
from rest_framework import mixins
from rest_framework.generics import get_object_or_404

from . import serializers
from . import models


class UserRegisterView(generics.CreateAPIView):
    """
    Register Users.
    """
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class ListCreateUserPrefs(mixins.CreateModelMixin, generics.RetrieveUpdateAPIView):
    """
    List or Create User Preferences.
    Endpoint: /api/user/preferences
    Methods: GET and PUT
    """
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        try:
            obj = models.UserPref.objects.get(user=self.request.user.id)
        except models.UserPref.DoesNotExist:
            obj = models.UserPref.objects.create(user=self.request.user)
        return obj

    def perform_update(self, serializer):
        serializer.save()


class GetNextUndecidedDog(generics.RetrieveAPIView):
    """
    Get next undecided dog.
    Endpoint: /api/dog/<pk>/undecided/next/
    Method: GET
    """
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_object(self):
        print(self.kwargs)

        undecided_dogs = []
        for dog in models.Dog.objects.all():
            undecided_dogs.append(dog.id)

        print(undecided_dogs)

        next_dog = undecided_dogs[int(self.kwargs['pk'])-1]
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=next_dog)  # Lookup the object

        return obj



