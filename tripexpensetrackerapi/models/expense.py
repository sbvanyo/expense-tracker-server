from django.db import models
from django.utils import timezone
from .user import User
from .trip import Trip

class Expense(models.Model):
    name = models.CharField(max_length=51)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
