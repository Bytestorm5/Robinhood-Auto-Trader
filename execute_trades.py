import robin_stocks as r
from dotenv import load_dotenv
import sys
from datetime import datetime

load_dotenv()
from robin_trader import *

log_file = open(f"logs/output_log_{datetime.now().strftime('%d-%m-%Y')}.txt", "a")
def log_and_print(message):
    sys.stdout.write(message + '\n')
    log_file.write(message + '\n')
    log_file.flush()

AUTO_EXECUTE = any([auto_arg in sys.argv for auto_arg in ['-a', '--auto']])
CANCEL_ALL = any([auto_arg in sys.argv for auto_arg in ['-c', '--cancel', '--cancel-all']])

if not AUTO_EXECUTE:
    awknowledgement = """By using this tool I accept any and all responsibility for gains or losses caused by this tool.\nI awknowledge and accept that the repository owner, and any contributors, holds no responsibility for any of my gains or losses caused by this tool."""
    log_and_print(awknowledgement)
    response = input("Accept? (Y/*)")
    if response.lower() != 'y':
        exit()
else:
    log_and_print("Auto flag present- skipped awknowledgement.")

def buy(symbol: str, shares: float, limit: float | None):
    if limit == None:
        log_and_print(f"BUY  {symbol} @ MARKET: {shares}")
    else:
        log_and_print(f"BUY  {symbol} @ >= {limit}: {shares}")
    if not AUTO_EXECUTE and (CANCEL_ALL or input("Execute? (Y/*)").lower() != 'y'):
        log_and_print(" - Order Canceled")
        return False
    else:
        if limit == None:
            r.order_buy_market(symbol, quantity, timeInForce='ioc')
        else:
            r.order_buy_limit(symbol, quantity, limit, timeInForce='gfd')
        log_and_print(" - Order Placed")
        return True

def sell(symbol: str, shares: float, limit: float | None):
    if limit == None:
        log_and_print(f"SELL  {symbol} @ MARKET: {shares}")
    else:
        log_and_print(f"SELL  {symbol} @ >= {limit}: {shares}")
    if not AUTO_EXECUTE and (CANCEL_ALL or input("Execute? (Y/*)").lower() != 'y'):
        log_and_print(" - Order Canceled")
        return False
    else:
        if limit == None:
            r.order_sell_market(symbol, quantity, timeInForce='ioc')
        else:
            r.order_sell_limit(symbol, quantity, limit, timeInForce='gfd')
        log_and_print(" - Order Placed")
        return True
    
holdings = r.build_holdings()
profile = r.build_user_profile()

FUNDS = float(profile['cash'])
symbols = PARAMS['STOCK_POOL'].split()

all_symbols = list(set(symbols + list(holdings.keys())))

softmax_sum = sum([np.exp(float(holdings.get(symbol, {'percent_change':0})['percent_change'])) for symbol in all_symbols])
portions = {}
for symbol in all_symbols:
    portions[symbol] = np.exp(float(holdings.get(symbol, {'percent_change':0})['percent_change'])) / softmax_sum

BUY_AMOUNT = FUNDS / len(symbols)
for symbol in all_symbols:
    highs, lows, hist = high_low_history(symbol)
    action = determine_action(highs, lows, hist)

    BUY_AMOUNT = FUNDS * portions[symbol] #/ len(symbols)

    # Only Buy if there are sufficient funds and this is a stock we want to buy
    # All other stocks should *eventually* be sold- when the time is right
    if action > 0 and FUNDS > PARAMS['MIN_FUNDS'] and symbol in symbols:
        to_spend = min((BUY_AMOUNT * action), FUNDS*0.9)
        quantity = to_spend / hist[-1]

        if buy(symbol, quantity, hist[-1]):
            FUNDS -= to_spend * 1.05
    elif symbol in holdings and (action < 0 or float(holdings[symbol]['percent_change']) > (PARAMS['MAX_PROFIT_RATIO'] - 1)):
        sell_ratio = min(0.15 + np.sqrt(-action), PARAMS['MAX_SELL_PROPORTION'])

        gain = sell_ratio * float(holdings[symbol]['quantity']) * hist[-1]
        cost = sell_ratio * float(holdings[symbol]['average_buy_price']) * float(holdings[symbol]['quantity'])

        if (gain*0.95) / cost >= PARAMS['MIN_PROFIT_RATIO']:
            quantity = float(holdings[symbol]['quantity']) * sell_ratio
            
            if sell(symbol, quantity, hist[-1]):
                FUNDS += gain * 0.95
        else:
            log_and_print(f"HOLD {symbol}")
    else:
        log_and_print(f"HOLD {symbol}")

log_file.close()