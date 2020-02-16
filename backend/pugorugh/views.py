from django.contrib.auth import get_user_model

from rest_framework import permissions
from rest_framework import generics

from . import serializers
from . import models


class UserRegisterView(generics.CreateAPIView):
    """
    Register Users.
    """
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class ListCreateUserPrefs(generics.ListCreateAPIView):
    """
    List / Create User Preferences.
    """
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer


#
