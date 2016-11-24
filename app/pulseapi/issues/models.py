from django.db import models

# Create your models here.
class Issue(models.Model):
    """
    The Mozilla issues
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        return str(self.name)
        