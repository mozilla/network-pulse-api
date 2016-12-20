"""
Uncomment these lines to enable admin of Issues.
But you probably don't need to since they're fixed data.
"""
from django.contrib import admin

from .models import Issue

admin.site.register(Issue)
