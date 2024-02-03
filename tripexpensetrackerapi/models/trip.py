from django.db import models
from django.utils import timezone
from tripexpensetrackerapi.models import User
class Trip(models.Model):
    name = models.CharField(max_length=51)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
