from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView, UpdateView
from .models import Market, Order, Side

def home(request):
    return render(request, 'home.html')

@login_required
def markets(request):
    context = {
        'markets': [
            {
                'market': market,
                'buy_orders': Order.objects.filter(market=market, side=Side.BUY).order_by('price', 'date_time_ordered'),
                'sell_orders': Order.objects.filter(market=market, side=Side.SELL).order_by('price', '-date_time_ordered')
            }
            for market in Market.objects.all()
        ]
    }
    return render(request, 'markets.html', context=context)

'''
@login_required
def create_market(request):
    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Market successfully created.')
            return redirect('markets')
    else:
        form = MarketForm()
    return render(request, 'create_market.html', {'form': form})
'''

class MarketCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Market
    fields = ['description', 'details', 'min_value', 'max_value', 'tick_size', 'multiplier']
    success_url = '/markets/'
    success_message = 'Market successfully created.'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MarketUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Market
    fields = ['description', 'details', 'settlement']
    success_url = '/markets/'
    success_message = 'Market successfully updated.'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        market = self.get_object()
        return self.request.user == market.created_by
