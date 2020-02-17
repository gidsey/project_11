from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import generics
from . import mixins

from . import serializers
from . import models


class UserRegisterView(generics.CreateAPIView):
    """
    Register Users.
    """
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class ListCreateUserPrefs(mixins.AllowPUTAsCreateMixin, generics.RetrieveUpdateAPIView):
    """
    List / Create User Preferences.
    """
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer
    lookup_field = 'user'

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     obj = get_object_or_404(queryset, user=self.request.user)
    #     print(obj)
    #     return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
