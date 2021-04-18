from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import F
from .models import Account, Event, Group, Market, Order, Position, Side, Trade

class AccountManager:
    def add_user_to_group(group: Group, user: User):
        # create account for user
        account = Account(group=group, user=user)
        account.save()

    def increment_balance(group: Group, user: User, inc: Decimal):
        Account.objects.filter(group=group, user=user).update(balance=F('balance')+inc)

class OrderManager:
    def get_best_order(market: Market, on_side: Side):
        if on_side == Side.BUY:
            buy_set = Order.objects.filter(side=on_side, market=market).order_by('-price', 'time_ordered')
            if buy_set.count() == 0:
                return None
            return buy_set.first()
        else:
            sell_set = Order.objects.filter(side=on_side, market=market).order_by('price', 'time_ordered')
            if sell_set.count() == 0:
                return None
            return sell_set.first()
    
    def in_cross(buy_price, sell_price):
        return buy_price >= sell_price

    def add_order(market: Market, user: User, side: Side, price: Decimal):
        position = Position.objects.filter(market=market, user=user).first().position
        existing_orders = Order.objects.filter(market=market, ordered_by=user, side=side).count()
        if side == Side.SELL:
            existing_orders *= -1

        print(position, existing_orders, market.position_limit)

        if abs(position+existing_orders) >= market.position_limit:
            return 'The number of orders placed exceeds your position limit.'
        
        if price < market.min_price or price > market.max_price:
            return 'The price is out of bounds.'
        
        above_min = price-market.min_price

        if above_min % market.tick_size != Decimal(0):
            return 'The price is not a multiple of the tick-size.'
        
        best_match = OrderManager.get_best_order(market, Side.flip(side))

        if best_match is not None:
            if best_match.ordered_by == user:
                if side == Side.BUY and price >= best_match.price or side == Side.SELL and price <= best_match.price:
                    return 'The order is in-cross with another one of your orders.'
            
            if side == Side.BUY and price >= best_match.price:
                best_match.delete()
                TradeManager.add_trade(market, user, best_match.ordered_by, best_match.price, True)
                PositionManager.increment_position(market, user, 1)
                PositionManager.increment_position(market, best_match.ordered_by, -1)
                return 'Traded'
            elif side == Side.SELL and price <= best_match.price:
                best_match.delete()
                TradeManager.add_trade(market, best_match.ordered_by, user, best_match.price, False)
                PositionManager.increment_position(market, user, -1)
                PositionManager.increment_position(market, best_match.ordered_by, 1)
                return 'Traded'

        order = Order(side=side, market=market, ordered_by=user, price=price)
        order.save()

        return 'Order placed'

class PositionManager:
    def add_position(market: Market, user: User):
        position = Position(market=market, user=user)
        position.save()
    
    def increment_position(market: Market, user: User, inc: int):
        Position.objects.filter(market=market, user=user).update(position=F('position')+inc)

class TradeManager:
    def add_trade(market: Market, buyer: User, seller: User, price: Decimal, is_buyer_aggressor: bool):
        trade = Trade(market=market, price=price, buyer=buyer, seller=seller, is_buyer_aggressor=is_buyer_aggressor)
        trade.save()
