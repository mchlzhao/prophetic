from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Market(models.Model):
    description = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)

    date_time_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    min_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_value = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    tick_size = models.DecimalField(max_digits=8, decimal_places=2, default=1)

    settlement = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.description
