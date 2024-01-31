from django.db import models

class User(models.Model):
    name = models.CharField(max_length=51)
    uid = models.CharField(max_length=51)
