from django.db import models

class Trip(models.Model):
    name = models.CharField(max_length=51)
