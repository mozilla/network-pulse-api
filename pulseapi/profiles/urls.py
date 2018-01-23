from django.conf.urls import url

from pulseapi.profiles.views import (
    UserProfileAPIView,
    UserProfilePublicAPIView,
    UserProfilePublicSelfAPIView,
)

urlpatterns = [
    url(
        r'^(?P<pk>[0-9]+)/update/',
        UserProfileAPIView.as_view(),
        name='profile_update',
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
    )
]
