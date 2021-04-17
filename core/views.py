from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from .logic import AccountManager
from .forms import EventCreateForm, OrderForm
from .models import Account, Event, Group, Market, Order, Side

def home(request):
    return render(request, 'home.html')

@login_required
def group_list(request):
    group_ids = Account.objects.filter(user=request.user).values('group_id').distinct()
    context = {
        'groups': Group.objects.filter(id__in=group_ids).order_by('name'),
    }
    return render(request, 'group_list.html', context)

class GroupCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Group
    fields = ['name']
    success_url = '/groups/'
    success_message = 'Group successfully created.'

    def form_valid(self, form):
        group = form.save(commit=False)
        group.created_by = self.request.user
        group.save()

        AccountManager.add_user_to_group(group, self.request.user)
        return redirect('group_list')

@login_required
def event_list(request, group_id):
    if Account.objects.filter(user=request.user, group=group_id).count() == 0:
        return HttpResponseForbidden()

    group = Group.objects.get(pk=group_id)
    context = {
        'events': Event.objects.filter(group=group_id).order_by('name'),
        'group': group,
    }
    return render(request, 'event_list.html', context)

@login_required
def event_create(request, group_id):
    if Account.objects.filter(user=request.user, group=group_id).count() == 0:
        return HttpResponseForbidden()

    group = Group.objects.get(pk=group_id)
    form = EventCreateForm()
    if request.method == 'POST':
        form = EventCreateForm(request.POST)
        if form.is_valid():
            form.save(group_id=group_id, created_by=request.user)
            return HttpResponseRedirect(reverse('event_list', args=(group_id, )))
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'event_create.html', context)

@login_required
def markets(request):
    context = {
        'markets': [
            {
                'market': market,
                'buy_orders': Order.objects.filter(market=market, side=Side.BUY).order_by('-price', 'time_ordered'),
                'sell_orders': Order.objects.filter(market=market, side=Side.SELL).order_by('-price', '-time_ordered'),
                'order_form': OrderForm(),
            }
            for market in Market.objects.all()
        ],
    }
    if request.is_ajax():
        return render(request, 'markets_list.html', context)

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save(market_id=request.POST.get('market_id'), ordered_by=request.user)
            return redirect('markets')

    return render(request, 'markets.html', context)

class MarketCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Market
    fields = ['description', 'details', 'min_price', 'max_price', 'tick_size', 'multiplier', 'position_limit']
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

@login_required
def order_delete(request):
    order = Order.objects.get(pk=request.GET['order_id'])
    if order.ordered_by != request.user:
        return HttpResponse('Permission denied')
    order.delete()
    return HttpResponse('OK')

@login_required
def get_market_orders(request):
    def order_to_json(order):
        return {
            'pk': order.pk,
            'ordered_by': order.ordered_by.username,
            'price': order.price,
        }

    orders = dict()
    for market in Market.objects.all():
        buy_orders = Order.objects.select_related('ordered_by').filter(market=market, side=Side.BUY).order_by('-price', 'time_ordered')
        buy_orders_json = [order_to_json(order) for order in buy_orders]
        sell_orders = Order.objects.filter(market=market, side=Side.SELL).order_by('-price', '-time_ordered')
        sell_orders_json = [order_to_json(order) for order in sell_orders]
        orders[market.pk] = {
            'buy_orders': buy_orders_json,
            'sell_orders': sell_orders_json,
        }

    return JsonResponse(orders)
