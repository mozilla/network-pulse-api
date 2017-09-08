from django.conf.urls import url

from pulseapi.profiles.views import (
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
    )
]
