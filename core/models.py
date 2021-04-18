from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    time_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'name'],
                name='unique_event_name_per_group',
            )
        ]

class Market(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    description = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    time_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    min_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_price = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    tick_size = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    multiplier = models.PositiveIntegerField(default=1)
    position_limit = models.IntegerField(default=5)

    settlement = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.description

class Side(models.TextChoices):
    BUY = 'buy', 'Buy'
    SELL = 'sell', 'Sell'

class Order(models.Model):
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    ordered_by = models.ForeignKey(User, on_delete=models.PROTECT)
    side = models.CharField(max_length=4, choices=Side.choices)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    time_ordered = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Order on {self.market} by {self.ordered_by}, {self.side} at {self.price}'

class Position(models.Model):
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    position = models.IntegerField(default=0) # positive is long, negative is short

class Trade(models.Model):
    market = models.ForeignKey(Market, on_delete=models.PROTECT)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='buyer_user')
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name='seller_user')
    is_buyer_aggressor = models.BooleanField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    time_traded = models.DateTimeField(default=timezone.now)

class Account(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'user'],
                name='unique_user_per_group',
            )
        ]
