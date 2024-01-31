from django.db import models
from .expense import Expense
from .category import Category

class ExpenseCategory(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
