from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from .logic import *
from .forms import EventCreateForm
from .models import Account, Event, Group, Market, Order, Side

def home(request):
    return render(request, 'home.html')

@login_required
def group_list(request):
    group_ids = Account.objects.filter(user=request.user).values('group_id').distinct()
    context = {
        'groups': Group.objects.filter(id__in=group_ids).order_by('name')
    }
    return render(request, 'group_list.html', context)

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ['name']
    success_url = '/groups/'

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
        'group': group
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
        'group': group
    }
    return render(request, 'event_form.html', context)

@login_required
def markets(request, event_id):
    event = Event.objects.get(pk=event_id)
    if Account.objects.filter(user=request.user, group=event.group).count() == 0:
        return HttpResponseForbidden()

    event = Event.objects.get(pk=event_id)
    markets_list = Market.objects.filter(event=event_id)
    context = {
        'event': event,
        'group': event.group,
        'markets': [
            {
                'has_settled': market.settlement is not None,
                'market': market,
                'buy_orders': Order.objects.filter(market=market, side=Side.BUY).order_by('-price', 'time_ordered'),
                'sell_orders': Order.objects.filter(market=market, side=Side.SELL).order_by('-price', '-time_ordered')
            }
            for market in markets_list
        ],
    }
                
    return render(request, 'markets.html', context)

class MarketCreateView(LoginRequiredMixin, CreateView):
    model = Market
    fields = ['description', 'details', 'min_price', 'max_price', 'tick_size', 'multiplier', 'position_limit']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        event = Event.objects.get(pk=self.kwargs['event_id'])
        form.instance.event = event
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('markets', kwargs={'event_id': self.kwargs['event_id']})
    
    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        MarketPositionManager.add_positions_for_market(self.object)
        return ret

class MarketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Market
    fields = ['description', 'details', 'settlement']

    def get_success_url(self):
        return reverse('markets', kwargs={'event_id': self.kwargs['event_id']})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        prev_settlement = self.object.settlement
        ret = super().post(request, *args, **kwargs)
        cur_settlement = self.object.settlement
        MarketManager.settle(self.object, prev_settlement, cur_settlement)
        return ret

    def test_func(self):
        market = self.get_object()
        return self.request.user == market.created_by

@login_required
def order_add(request):
    market = Market.objects.get(pk=request.POST['market_id'])
    if Account.objects.filter(group=market.event.group, user=request.user).count() == 0:
        return HttpResponseForbidden()

    side = Side.BUY if request.POST['is_buy'] == 'true' else Side.SELL
    if len(request.POST['price']) == 0:
        return HttpResponse('Price is not numeric.')
    try:
        x = float(request.POST['price'])
    except ValueError:
        return HttpResponse('Price is not numeric.')
    
    def decimal_places(s):
        c = s.split('.')
        if len(c) == 1:
            return 0
        return len(c[1])

    dp = decimal_places(request.POST['price'])
    if dp > 2:
        return HttpResponse('Price has too many decimal places.')
    
    price = Decimal(request.POST['price'])

    response = OrderManager.add_order(market, request.user, side, price)

    return HttpResponse(response)
    
@login_required
def order_delete(request):
    order = Order.objects.get(pk=request.GET['order_id'])
    if order.ordered_by != request.user:
        return HttpResponse('Permission denied')
    order.delete()
    return HttpResponse('Order deleted')

@login_required
def get_market_orders_and_position(request, event_id):
    def order_to_json(order):
        return {
            'pk': order.pk,
            'ordered_by': order.ordered_by.username,
            'price': order.price
        }

    event = Event.objects.get(pk=event_id)
    markets_list = Market.objects.filter(event=event_id)
    orders = dict()
    for market in markets_list:
        buy_orders = Order.objects.select_related('ordered_by').filter(market=market, side=Side.BUY).order_by('-price', 'time_ordered')
        buy_orders_json = [order_to_json(order) for order in buy_orders]
        sell_orders = Order.objects.filter(market=market, side=Side.SELL).order_by('-price', '-time_ordered')
        sell_orders_json = [order_to_json(order) for order in sell_orders]
        pos = MarketPosition.objects.filter(market=market, user=request.user).first()
        orders[market.pk] = {
            'has_settled': market.settlement is not None,
            'settlement': market.settlement,
            'buy_orders': buy_orders_json,
            'sell_orders': sell_orders_json,
            'pos': pos.position,
            'abs_pos': abs(pos.position),
            'pnl': pos.profitLoss
        }

    return JsonResponse(orders)

@login_required
def event_accounts(request, event_id):
    event = Event.objects.get(pk=event_id)
    if Account.objects.filter(user=request.user, group=event.group).count() == 0:
        return HttpResponseForbidden()
    
    markets = Market.objects.filter(event=event).order_by('time_created')
    accounts = Account.objects.filter(group=event.group).order_by('-balance')

    event_balance = {account.user: 0 for account in accounts}
    positions = {}
    for position in MarketPosition.objects.filter(market__in=markets):
        positions[(position.market, position.user)] = position.position
        event_balance[position.user] += position.profitLoss

    def get_markets_row(market):
        return {
            'description': market.description,
            'positions': [
                {
                    'pos': positions[(market, account.user)],
                    'abs_pos': abs(positions[(market, account.user)])
                }
                for account in accounts
            ]
        }

    context = {
        'accounts': [
            {
                'name': account.user.username,
                'balance': account.balance,
                'event_balance': event_balance[account.user]
            } for account in accounts
        ],
        'event': event,
        'markets': [
            get_markets_row(market)
            for market in markets
        ]
    }

    if request.is_ajax():
        return render(request, 'accounts_table.html', context)

    return render(request, 'accounts.html', context)

@login_required
def add_member(request, group_id):
    group = Group.objects.get(pk=group_id)
    if Account.objects.filter(group=group, user=request.user).count() == 0:
        return HttpResponseForbidden()
    
    return render(request, 'group_add_member.html', {'group': group})

@login_required
def add_member_ajax(request, group_id):
    group = Group.objects.get(pk=group_id)
    if Account.objects.filter(group=group, user=request.user).count() == 0:
        return HttpResponseForbidden()
    
    username = str(request.POST['username'])
    new_user = User.objects.filter(username=username).first()
    if new_user == None:
        return HttpResponse('Username does not exist')
    if Account.objects.filter(group=group, user=new_user).count() > 0:
        return HttpResponse('User is already part of group')
    
    AccountManager.add_user_to_group(group, new_user)
    return HttpResponse('User added')
