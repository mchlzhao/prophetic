from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView, UpdateView
from .models import Market

def home(request):
    return render(request, 'home.html')

@login_required
def markets(request):
    return render(request, 'markets.html', context={'markets': Market.objects.all()})

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
    fields = ['description', 'details', 'min_value', 'max_value', 'tick_size', 'settlement']
    success_url = '/markets/'
    success_message = 'Market successfully created.'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MarketUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Market
    fields = ['description', 'details', 'min_value', 'max_value', 'tick_size', 'settlement']
    success_url = '/markets/'
    success_message = 'Market successfully updated.'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        market = self.get_object()
        return self.request.user == market.created_by
