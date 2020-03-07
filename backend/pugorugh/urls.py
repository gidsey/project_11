from django.conf.urls import url
from django.urls import path, re_path, register_converter
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from . import views, converters

register_converter(converters.StatusConverter, 'ds')
# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^api/user/login/$', obtain_auth_token, name='login-user'),
    url(r'^api/user/$', views.UserRegisterView.as_view(), name='register-user'),
    url(r'^favicon\.ico$',
        RedirectView.as_view(
            url='/static/icons/favicon.ico',
            permanent=True
        )),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    path('api/user/preferences/', views.UserPrefs.as_view(), name='user-prefs'),
    path('api/dog/<pk>/undecided/next/', views.UndecidedDogs.as_view(), name='next_undecided'),
    path('api/dog/<pk>/<ds:status>/next/', views.ChosenDogs.as_view(), name='next-chosen'),
    path('api/dog/<int:pk>/<ds:status>/', views.SetStatus.as_view(), name='set_status'),

])
