from dotenv import load_dotenv
import numpy as np
from tqdm import tqdm
import os
load_dotenv()

from robin_trader import determine_action, history, high_low_history_with_dates
import robin_trader
from datetime import datetime, timedelta

histories = {}
history_length = 0
last_history_update = datetime.now()

def sim_trades(START_FUNDS, custom_symbols: list[str] | None = None, flip = False):
    global histories, history_length, last_history_update
    symbols = os.environ.get("STOCK_POOL").split() if custom_symbols == None else custom_symbols
    symbols = list(set(symbols)) # Just in case

    AVAILABLE_FUNDS = START_FUNDS
    START = max(robin_trader.PARAMS['RSI_PERIOD'], robin_trader.PARAMS['MAC_WINDOW'], robin_trader.PARAMS['STDDEV_WINDOW'], robin_trader.PARAMS['MAC_VISION'], robin_trader.PARAMS['BOLLINGER_WINDOW'])

    positions = {}
    costs = {}
    rois = {}
    last_trade = {}

    for symbol in symbols:
        if symbol not in histories or datetime.now() - last_history_update > timedelta(hours=1):
            histories[symbol] = high_low_history_with_dates(symbol, span='year')
            history_length = max(history_length, len(histories[symbol][0]))

        positions[symbol] = 0
        costs[symbol] = 0

    available_graph = [START_FUNDS]
    available_graph_with_nonliquid = [START_FUNDS]

    for i in tqdm(list(range(START, history_length))):        
        available_graph_with_nonliquid.append(0)

        softmax_sum = 0

        for symbol in symbols:
            hist, highs, lows, dates = histories[symbol]
            hist = hist[:i]

            gain = positions[symbol] * hist[-1]
            cost = costs[symbol]
            rois[symbol] = gain / cost if cost > 0 else 1
            softmax_sum += np.exp(rois[symbol])
        
        portions = {}
        for symbol in symbols:
            portions[symbol] = np.exp(rois[symbol]) / softmax_sum

        for symbol in symbols:
            hist, highs, lows, dates = histories[symbol]
            hist = hist[:i]
            highs = highs[:i]
            lows = lows[:i]
            action = determine_action(highs, lows, hist)        
            if flip:
                action *= -1    

            BUY_AMOUNT = AVAILABLE_FUNDS * portions[symbol]

            # Buy
            if action > 0 and AVAILABLE_FUNDS > robin_trader.PARAMS['MIN_FUNDS']:
                to_spend = min((BUY_AMOUNT * action), AVAILABLE_FUNDS*0.9)
                quantity = to_spend / (hist[-1] * 1.05)
                
                costs[symbol] += to_spend
                AVAILABLE_FUNDS -= to_spend
                positions[symbol] += quantity
                # print(f"BUY {quantity} {symbol} @ {hist[-1]}")
            # Sell
            elif positions[symbol] > 0 and (action < 0 or rois[symbol] >= robin_trader.PARAMS['MAX_PROFIT_RATIO']) and i - last_trade.get(symbol, -3) > 3:
                sell_ratio = min(min(0.15 + np.sqrt(-action), 1) if action < 0 else 1, robin_trader.PARAMS.get('MAX_SELL_PROPORTION', 1))

                gain = sell_ratio * positions[symbol] * hist[-1] * 0.95
                cost = sell_ratio * costs[symbol]

                if gain / cost >= robin_trader.PARAMS['MIN_PROFIT_RATIO']:
                    #print(f"SELL {positions[symbol]} {symbol} @ {hist[-1]}")
                    positions[symbol] *= 1 - sell_ratio
                    costs[symbol] *= 1 - sell_ratio
                    AVAILABLE_FUNDS += gain                  
            
            available_graph_with_nonliquid[-1] += positions[symbol] * hist[-1]
        available_graph.append(AVAILABLE_FUNDS)
        available_graph_with_nonliquid[-1] += AVAILABLE_FUNDS
    print(portions)
    return available_graph_with_nonliquid, available_graph, dates[START:]

if __name__ == "__main__":
    sim_trades(4000)