"""pulseapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    # base patterns
    url(r'^admin/', admin.site.urls),

    # new patterns
    url(r'^api/pulse/', include('pulseapi.users.urls')),
    url(r'^api/pulse/entries/', include('pulseapi.entries.urls')),
    url(r'^api/pulse/tags/', include('pulseapi.tags.urls')),
    url(r'^api/pulse/issues/', include('pulseapi.issues.urls')),
    url(r'^api/pulse/creators/', include('pulseapi.creators.urls')),

    # deprecated patterns
    url(r'^', include('pulseapi.users.urls')),
    url(r'^entries/', include('pulseapi.entries.urls')),
    url(r'^tags/', include('pulseapi.tags.urls')),
    url(r'^issues/', include('pulseapi.issues.urls')),
    url(r'^helptypes/', include('pulseapi.helptypes.urls')),
    url(r'^creators/', include('pulseapi.creators.urls')),
]

if settings.USE_S3 is not True:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
