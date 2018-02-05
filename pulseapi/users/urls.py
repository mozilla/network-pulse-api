from django.conf.urls import url

from . import views
from pulseapi.utility.urlutils import versioned_url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.start_auth, name='login'),
    url(r'^logout', views.force_logout, name='logout'),
    url(r'^oauth2callback', views.callback, name='oauthcallback'),
    url(r'^nonce', views.nonce, name="get a new nonce value"),
    # /api/pulse/<version pattern>/userstatus
    url(versioned_url(r'^') + 'userstatus', views.userstatus, name="get current user information"),
    # /api/pulse/status/
    url(r'^status/', views.api_status, name='api-status'),
]
