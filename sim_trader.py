from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
load_dotenv()

from robin_trader import determine_action, history
import robin_trader
from datetime import datetime, timedelta

histories = {}
history_length = 0
last_history_update = datetime.now()

def sim_trades(START_FUNDS, custom_symbols: list[str] | None = None):
    global histories, history_length, last_history_update
    symbols = os.environ.get("STOCK_POOL").split() if custom_symbols == None else custom_symbols
    symbols = list(set(symbols)) # Just in case

    AVAILABLE_FUNDS = START_FUNDS
    START = robin_trader.PARAMS['EXIT_MACD_LONG_PERIOD']

    positions = {}
    costs = {}

    for symbol in symbols:
        if symbol not in histories or datetime.now() - last_history_update > timedelta(hours=1):
            histories[symbol] = history(symbol)
            history_length = max(history_length, len(histories[symbol]))

        positions[symbol] = 0
        costs[symbol] = 0

    available_graph = [START_FUNDS]
    available_graph_with_nonliquid = [START_FUNDS]

    for i in tqdm(list(range(START, history_length))):
        BUY_AMOUNT = (AVAILABLE_FUNDS / len(symbols))
        available_graph_with_nonliquid.append(0)
        for symbol in symbols:
            hist = histories[symbol][:i]
            action = determine_action(hist)                

            gain = positions[symbol] * hist[-1]
            cost = costs[symbol]

            # Buy
            if action > 0 and AVAILABLE_FUNDS > robin_trader.PARAMS['MIN_FUNDS']:
                to_spend = min((BUY_AMOUNT * action), AVAILABLE_FUNDS*0.9)
                quantity = to_spend / (hist[-1] * 1.05)
                
                costs[symbol] += to_spend
                AVAILABLE_FUNDS -= to_spend
                positions[symbol] += quantity
                # print(f"BUY {quantity} {symbol} @ {hist[-1]}")
            # Sell
            elif positions[symbol] > 0 and (action < 0 or gain / cost >= robin_trader.PARAMS['MAX_PROFIT_RATIO']):               
                sell_ratio = min(0.15 + np.sqrt(-action), 1)

                gain = sell_ratio * positions[symbol] * hist[-1] * 0.95
                cost = sell_ratio * costs[symbol]

                if gain / cost >= robin_trader.PARAMS['MIN_PROFIT_RATIO']:
                    # print(f"SELL {positions[symbol]} {symbol} @ {hist[-1]}")
                    positions[symbol] *= 1 - sell_ratio
                    costs[symbol] *= 1 - sell_ratio
                    AVAILABLE_FUNDS += gain                  
            
            available_graph_with_nonliquid[-1] += positions[symbol] * hist[-1]
        available_graph.append(AVAILABLE_FUNDS)
        available_graph_with_nonliquid[-1] += AVAILABLE_FUNDS
    
    return available_graph_with_nonliquid, list(range(START, history_length))
