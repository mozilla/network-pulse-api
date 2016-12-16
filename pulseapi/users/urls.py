from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout', views.force_logout, name='logout'),
    url(r'^oauth2callback', views.callback, name='oauthcallback'),
    
    # test routes
    url(r'^post', views.post_test, name="POST test"),
]
