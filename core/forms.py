from django import forms
from django.contrib.auth.models import User
from .models import Event, Group, Market, Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['side', 'price']

    def save(self, market_id, ordered_by):
        m = super().save(commit=False)
        self.instance.market = Market.objects.get(pk=market_id)
        self.instance.ordered_by = ordered_by
        m.save()

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name']
    
    def save(self, group_id, created_by):
        e = super().save(commit=False)
        self.instance.group = Group.objects.get(pk=group_id)
        self.instance.created_by = created_by
        e.save()
