from django.contrib import admin
from .models import Group, Event, Market, Order, Position, Trade, Account

admin.site.register(Group)
admin.site.register(Event)
admin.site.register(Market)
admin.site.register(Order)
admin.site.register(Position)
admin.site.register(Trade)
admin.site.register(Account)