from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse
from django.core.validators import MinValueValidator


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=False)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=False)
    added_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('items')
