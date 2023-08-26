import robin_stocks as r
from robin_trader import *
import sys

AUTO_EXECUTE = any([auto_arg in sys.argv for auto_arg in ['-a', '--auto']])
CANCEL_ALL = any([auto_arg in sys.argv for auto_arg in ['-c', '--cancel', '--cancel-all']])

def buy(symbol: str, shares: float):
    print(f"BUY  {symbol} @ MARKET: {shares}")
    if not AUTO_EXECUTE and (CANCEL_ALL or input("Execute? (Y/*)").lower() != 'y'):
        print(" - Order Canceled")
        return False
    else:
        r.order_buy_market(symbol, quantity, timeInForce='ioc')
        print(" - Order Placed")
        return True

def sell(symbol: str, shares: float):
    print(f"SELL  {symbol} @ MARKET: {shares}")
    if not AUTO_EXECUTE and (CANCEL_ALL or input("Execute? (Y/*)").lower() != 'y'):
        print(" - Order Canceled")
        return False
    else:
        r.order_sell_market(symbol, quantity, timeInForce='foc')
        print(" - Order Placed")
        return True
    
holdings = r.build_holdings()
profile = r.build_user_profile()

FUNDS = float(profile['cash'])
symbols = PARAMS['STOCK_POOL'].split()

BUY_AMOUNT = FUNDS / len(symbols)
for symbol in symbols + list(holdings.keys()):
    hist = history(symbol)
    action = determine_action(hist)

    # Only Buy if there are sufficient funds and this is a stock we want to buy
    # All other stocks should *eventually* be sold- when the time is right
    if action > 0 and FUNDS > PARAMS['MIN_FUNDS'] and symbol in symbols:
        to_spend = min((BUY_AMOUNT * action), FUNDS*0.9)
        quantity = to_spend / hist[-1]

        if buy(symbol, quantity):
            FUNDS -= to_spend * 1.05
    elif symbol in holdings and (action < 0 or float(holdings[symbol]['percent_change']) > (PARAMS['MAX_PROFIT_RATIO'] - 1)):
        sell_ratio = min(0.15 + np.sqrt(-action), PARAMS['MAX_SELL_PROPORTION'])

        gain = sell_ratio * float(holdings[symbol]['equity']) * hist[-1]
        cost = sell_ratio * float(holdings[symbol]['average_buy_price']) * float(holdings[symbol]['quantity'])

        if (gain*0.95) / cost >= PARAMS['MIN_PROFIT_RATIO']:
            quantity = float(holdings[symbol]['quantity']) * sell_ratio
            
            if sell(symbol, quantity, gain / quantity):
                FUNDS += gain * 0.95
    else:
        print(f"HOLD {symbol}")