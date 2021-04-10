from django import forms
from django.contrib.auth.models import User
from .models import Market, Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['side', 'price']

    def save(self, market_id, ordered_by):
        m = super().save(False)
        self.instance.market = Market.objects.get(pk=market_id)
        self.instance.ordered_by = ordered_by
        m.save()
