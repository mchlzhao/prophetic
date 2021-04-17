from django.contrib.auth.models import User
from django.db.models import F
from .models import Account, Event, Group, Market, Position

class AccountManager:
    def add_user_to_group(group, user):
        # create account for user
        account = Account(group=group, user=user)
        account.save()

    def increment_balance(group, user, inc):
        Account.objects.filter(group=group, user=user).update(balance=F('balance')+inc)

class PositionManager:
    def add_position(market, user):
        position = Position(market=market, user=user)
        position.save()
    
    def increment_position(market, user, inc):
        Position.objects.filter(market=market, user=user).update(position=F('position')+inc)

