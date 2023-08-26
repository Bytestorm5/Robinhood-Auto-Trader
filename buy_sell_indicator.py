import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import random

load_dotenv()

from robin_trader import determine_action, history, PARAMS

if __name__ == '__main__':
    symbols = PARAMS['STOCK_POOL'].split()
    # symbols = [
    #     'UMMA', 'HLAL', 'SPSK', 'SPRE', 'SPUS'
    # ]
    for symbol in symbols:
        action = determine_action(history(symbol, span='year'))
        if action > 0:
            print(f"{symbol}: Buy ({str(action*100)[:5]}%)")
        elif action == 0:
            print(f"{symbol}: Hold")
        elif action < 0:
            print(f"{symbol}: Sell ({str(action*-100)[:5]}%)")