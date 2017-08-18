from django.conf.urls import url

from pulseapi.profiles.views import (
    UserProfileChangeAPIView,
)

urlpatterns = [
    url(
        r'^myprofile/',
        UserProfileChangeAPIView.as_view(),
        name='profile'
    )
]
