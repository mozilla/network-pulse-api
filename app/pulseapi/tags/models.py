from django.db import models

# Create your models here.
class Tag(models.Model):
    """
    Tags used to describe properties of an entry and to
    enable filtering entries by these properties
    """
    name = models.CharField(unique=True, max_length=150)

    def __str__(self):
        return str(self.name)
        