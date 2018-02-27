from django.conf.urls import url

from pulseapi.profiles.views import (
    # UserProfileAPIView, # see note below.
    UserProfileListAPIView,
    UserProfilePublicAPIView,
    UserProfilePublicSelfAPIView,
    UserProfileEntriesAPIView,
)

urlpatterns = [
    url(
        r'^(?P<pk>[0-9]+)/entries/',
        UserProfileEntriesAPIView.as_view(),
        name='profile-entries',
    ),
    url(
        r'^(?P<pk>[0-9]+)/',
        UserProfilePublicAPIView.as_view(),
        name='profile',
    ),
    url(
        r'^me/',
        UserProfilePublicSelfAPIView.as_view(),
        name='profile_self',
    ),
    # note that there is also a /myprofile route
    # defined in the root urls.py which connects
    # to the UserProfileAPIView class.
    url(
        r'^$',
        UserProfileListAPIView.as_view(),
        name='profile_list',
    ),
]
