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

from pulseapi.profiles.views import UserProfileAPIView
from pulseapi.utility.syndication import (
    RSSFeedLatestFromPulse,
    AtomFeedLatestFromPulse,
    RSSFeedFeaturedFromPulse,
    AtomFeedFeaturedFromPulse
)
from pulseapi.utility.urlutils import (
    versioned_url,
    api_url,
    versioned_api_url,
)


rss_patterns = [
    url(r'^latest', RSSFeedLatestFromPulse()),
    url(r'^featured', RSSFeedFeaturedFromPulse()),
]

atom_patterns = [
    url(r'^latest', AtomFeedLatestFromPulse()),
    url(r'^featured', AtomFeedFeaturedFromPulse()),
]

urlpatterns = [
    # admin patterns
    url(r'^admin/', admin.site.urls),

    # 'homepage'
    url(r'^', include('pulseapi.users.urls')),

    # API routes
    url(api_url(), include('pulseapi.users.urls')),  # Non-versioned API url - r'^api/pulse/'
    url(versioned_api_url(r'entries/'), include('pulseapi.entries.urls')),
    url(versioned_api_url(r'profiles/'), include('pulseapi.profiles.urls')),
    url(versioned_api_url(r'tags/'), include('pulseapi.tags.urls')),
    url(versioned_api_url(r'issues/'), include('pulseapi.issues.urls')),
    url(versioned_api_url(r'helptypes/'), include('pulseapi.helptypes.urls')),
    url(versioned_api_url(r'creators/'), include('pulseapi.creators.urls')),

    # We provide an alternative route on the main `/api/pulse` route to allow
    # getting and editing a user's profile for the currently authenticated user
    url(
        versioned_api_url(r'myprofile/'),
        UserProfileAPIView.as_view(),
        name='myprofile'
    ),

    # Syndication
    url(versioned_url(r'^rss/'), include(rss_patterns)),  # r'^rss/<optional version>/'
    url(versioned_url(r'^atom/'), include(atom_patterns)),  # r'^atom/<optional version>/'
]

if settings.USE_S3 is not True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
