from django.conf.urls import url

from pulseapi.profiles.views import UserProfileRetrieveAPIView

urlpatterns = [
    url(
        r'^(?P<pk>[0-9]+)/',
        UserProfileRetrieveAPIView.as_view(),
        name='profile'
    )
]
