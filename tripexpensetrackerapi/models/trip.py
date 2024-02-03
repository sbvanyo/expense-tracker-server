from django.db import models
from tripexpensetrackerapi.models import User
class Trip(models.Model):
    name = models.CharField(max_length=51)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
