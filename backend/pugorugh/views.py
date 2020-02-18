from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import generics
from rest_framework import mixins

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
    List / Create User Preferences.
    """
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        try:
            obj = models.UserPref.objects.get(user=self.request.user.id)
        except models.UserPref.DoesNotExist:
            obj = models.UserPref.objects.create(user=self.request.user)
        return obj

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
