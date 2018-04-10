from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.start_auth, name='login'),
    url(r'^logout', views.force_logout, name='logout'),
    url(r'^oauth2callback', views.callback, name='oauthcallback'),
    url(r'^nonce', views.nonce, name="nonce"),
    url(r'^userstatus', views.userstatus, name="user-status"),
    url(r'^status/', views.api_status, name='api-status'),
]
