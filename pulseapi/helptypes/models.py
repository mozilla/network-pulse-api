from django.db import models


class HelpType(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500)

    def __str__(self):
        return str(self.name)
