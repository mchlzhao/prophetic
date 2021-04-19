from django.contrib import admin
from .models import Group, Event, Market, Order, MarketPosition, Trade, Account

admin.site.register(Group)
admin.site.register(Event)
admin.site.register(Market)
admin.site.register(Order)
admin.site.register(MarketPosition)
admin.site.register(Trade)
admin.site.register(Account)