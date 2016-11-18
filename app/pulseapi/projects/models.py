"""Main project data"""

from django.db import models

# Create your models here.
class ProjectQuerySet(models.query.QuerySet):
    """
    A queryset for Projects which only returns projects
    that are 'Active', 'Completed' or 'Closed'
    """

    def public(self):
        return self

class Project(models.Model):
    """
    A pulse project
    """
    title = models.CharField(max_length=500)
    description = models.TextField()
    content_url = models.URLField()
    thumbnail_url = models.URLField()
    tags = models.CharField(max_length=500)
    objects = ProjectQuerySet.as_manager()

