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


class UndecidedDogs(RetrieveAPIView):
    """
    Get next undecided dog.
    Endpoint:
            /api/dog/<pk>/undecided/next/
    Method(s): GET
    """
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        user_prefs = models.UserPref.objects.all().get(user=self.request.user)
        liked_dogs = models.UserDog.objects.all().filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='l'))
        disliked_dogs = models.UserDog.objects.all().filter(
            Q(user__exact=self.request.user.id) &
            Q(status__exact='d'))

        age_prefs = user_prefs.age.split(',')
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
            Q(gender__in=user_prefs.gender.split(',')) &
            Q(size__in=user_prefs.size.split(',')))

        matched_dogs = matched_dogs.filter(
            Q(age__range=(b_lower, b_upper)) |
            Q(age__range=(y_lower, y_upper)) |
            Q(age__range=(a_lower, a_upper)) |
            Q(age__range=(s_lower, s_upper))
        )

        print('{} liked dogs'.format(len(liked_dogs)))
        print('Liked Dogs:{}'.format(liked_dogs))
        liked_dogs_ids = [dog.dog_id for dog in liked_dogs]
        print('liked_dogs_ids:{}'.format(liked_dogs_ids))

        print('{} disliked dogs'.format(len(disliked_dogs)))
        print('Disliked Dogs:{}'.format(disliked_dogs))
        disliked_dogs_ids = [dog.dog_id for dog in disliked_dogs]
        print('disliked_dogs_ids:{}'.format(disliked_dogs_ids))

        chosen_dogs = set(liked_dogs_ids + disliked_dogs_ids)
        print('chosen_dogs: {}'.format(chosen_dogs))

        print('{} matched dogs'.format(len(matched_dogs)))
        print('Matched Dogs:{}'.format(matched_dogs))

        undecided_dogs = matched_dogs.exclude(id__in=chosen_dogs)

        print('{} undecided dogs'.format(len(undecided_dogs)))
        print('Undecided Dogs:{}'.format(undecided_dogs))

        if not undecided_dogs:
            raise NotFound  # No matching dogs so raise 404
        else:
            return undecided_dogs

    def get_object(self):
        pk = int(self.kwargs['pk'])  # Initially set to -1
        dog = self.get_queryset().filter(id__gt=pk).first()  # Retrieve the dog with the next highest id
        if dog is not None:
            return dog
        else:
            return self.get_queryset().first()  # Loop back around


class ChosenDogs(RetrieveAPIView):
    """
    Get next liked / disliked dog.
    Endpoints:
            /api/dog/<pk>/liked/next/
            /api/dog/<pk>/disliked/next/
    Method(s): GET
    """
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        pass

    def get_object(self):
        pk = int(self.kwargs['pk'])  # Initially set to -1
        current_status = self.kwargs['status'][0]  # returns l, d or u
        pass

    #     liked_dogs = models.UserDog.objects.all().prefetch_related('dog').filter(
    #         Q(user__exact=self.request.user.id) &
    #         Q(status__exact='l'))
    #
    #     disliked_dogs = models.UserDog.objects.all().prefetch_related('dog').filter(
    #         Q(user__exact=self.request.user.id) &
    #         Q(status__exact='d'))
    #
    #     undecided_dogs = self.get_queryset.filter(
    #         Q(id__in=models.UserDog.objects.file)
    #
    #     pick_list = []
    #
    #     liked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
    #         Q(user__exact=self.request.user.id) &
    #         Q(status__exact='l'))]
    #     liked_dogs.sort(key=lambda x: x.id)
    #
    #     disliked_dogs = [UserDog.dog for UserDog in self.get_queryset().prefetch_related('dog').filter(
    #         Q(user__exact=self.request.user.id) &
    #         Q(status__exact='d'))]
    #     disliked_dogs.sort(key=lambda x: x.id)
    #
    #     appraised_dogs = liked_dogs + disliked_dogs
    #     undecided_dogs = [dog for dog in self.get_queryset() if dog not in appraised_dogs]
    #     Return
    #     only
    #     undecided
    #     dogs
    #     undecided_dogs.sort(key=lambda x: x.id)  # Sort each list by ID
    #
    #     print('{} undecided dogs'.format(len(undecided_dogs)))
    #     print('{} liked dogs'.format(len(liked_dogs)))
    #     print('{} disliked dogs'.format(len(disliked_dogs)))
    #
    #     if current_status == 'l':
    #         pick_list = [dog for dog in liked_dogs if dog.id > pk]  # Filtered list of liked_dogs
    #
    #     if current_status == 'd':
    #         pick_list = [dog for dog in disliked_dogs if dog.id > pk]  # Filtered list of disliked_dogs
    #
    #     if current_status == 'u':
    #         pick_list = [dog for dog in undecided_dogs if dog.id > pk]  # Filtered list of undecided
    #
    # try:
    #     dog = pick_list[0]  # Show the next dog
    #     return dog
    # except IndexError:
    #
    #     if current_status == 'l':
    #         try:
    #             return liked_dogs[0]  # Loop back around to 1st liked dog
    #         except IndexError:
    #             raise NotFound  # There are no liked dogs to show
    #
    #     if current_status == 'd':
    #         try:
    #             return disliked_dogs[0]  # Loop back around to 1st disliked dog
    #         except IndexError:
    #             raise NotFound  # There are no disliked dogs to show
    #
    #     if current_status == 'u':
    #         try:
    #             return undecided_dogs[0]  # Loop back around to 1st undecided dog
    #         except IndexError:
    #             raise NotFound  # There are no undecided dogs to show
