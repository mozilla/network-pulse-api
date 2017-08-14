from django.db import models


# Create your models here.
class IssueQuerySet(models.query.QuerySet):
    """
    A queryset for issues which returns all issues
    """

    def public(self):
        """
        Returns all issues
        """
        return self

    def slug(self, slug):
        return self.filter(name=slug)


class Issue(models.Model):
    """
    The Mozilla issues
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    objects = IssueQuerySet.as_manager()

    def __str__(self):
        return str(self.name)
