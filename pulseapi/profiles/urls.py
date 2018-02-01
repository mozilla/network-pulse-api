from django.conf.urls import url

from pulseapi.profiles.views import (
    # UserProfileAPIView, # see note below.
    UserProfileAPISearchView,
    UserProfilePublicAPIView,
    UserProfilePublicSelfAPIView,
)

urlpatterns = [
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
        r'^search/',
        UserProfileAPISearchView.as_view(),
        name='profile_search',
    ),
]
