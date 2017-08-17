from django.conf.urls import url

from pulseapi.profiles.views import (
    ProfileView,
)

urlpatterns = [
    url(
        r'^(?P<pk>[0-9]+)/',
        ProfileView.as_view(),
        name='profile'
    )
]
