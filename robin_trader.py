import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import pyotp

PARAMS = {}

def refresh_params():
    load_dotenv()
    PARAMS['RSI_PERIOD'] = int(os.environ.get('RSI_PERIOD', 8))
    
    # PARAMS['ENTRY_MACD_SHORT_PERIOD'] = int(os.environ.get('ENTRY_MACD_SHORT_PERIOD', 12))
    # PARAMS['ENTRY_MACD_LONG_PERIOD'] = int(os.environ.get('ENTRY_MACD_LONG_PERIOD', 26))
    # PARAMS['ENTRY_MACD_SIGNAL_PERIOD'] = int(os.environ.get('ENTRY_MACD_SIGNAL_PERIOD', 9))
    
    # PARAMS['EXIT_MACD_SHORT_PERIOD'] = int(os.environ.get('EXIT_MACD_SHORT_PERIOD', 15))
    # PARAMS['EXIT_MACD_LONG_PERIOD'] = int(os.environ.get('EXIT_MACD_LONG_PERIOD', 39))
    # PARAMS['EXIT_MACD_SIGNAL_PERIOD'] = int(os.environ.get('EXIT_MACD_SIGNAL_PERIOD', 9))

    PARAMS['MAC_WINDOW'] = int(os.environ.get('MAC_WINDOW', 10))
    PARAMS['MAC_VISION'] = int(os.environ.get('MAC_VISION', 5))
    PARAMS['STDDEV_WINDOW'] = int(os.environ.get('STDDEV_WINDOW', 20))

    PARAMS['MIN_FUNDS'] = float(os.environ.get('MIN_FUNDS', 50))
    PARAMS['MAX_SELL_PROPORTION'] = float(os.environ.get("MAX_SELL_PROPORTION", 1.0))
    PARAMS['MAX_PROFIT_RATIO'] = float(os.environ.get("MAX_PROFIT_RATIO", 1.5))
    PARAMS['MIN_PROFIT_RATIO'] = float(os.environ.get("MIN_PROFIT_RATIO", 1.3))

    PARAMS['BOLLINGER_WINDOW'] = int(os.environ.get("BOLLINGER_WINDOW", ""))
    PARAMS['BOLLINGER_STD_MULT'] = float(os.environ.get("BOLLINGER_STD_MULT", ""))

    PARAMS['STOCK_POOL'] = os.environ.get("STOCK_POOL", "")

    # PARAMS['EMAIL'] = os.environ.get("EMAIL")
    # PARAMS['PASSWORD'] = os.environ.get("PASSWORD")
    # PARAMS['OTP_CODE'] = os.environ.get("OTP_CODE")


refresh_params()
login = r.login(os.environ.get("EMAIL"), os.environ.get("PASSWORD"), mfa_code=pyotp.TOTP(os.environ.get("OTP_CODE")).now())

def calculate_bollinger(prices, window=20, std_prod=2):
    # Convert the price data to a pandas DataFrame
    data = pd.DataFrame({'Price': prices})
    data['SMA'] = data['Price'].rolling(window=window).mean()
    data['std'] = data['Price'].rolling(window=window).std()
    data['Upper_Band'] = data['SMA'] + std_prod * data['std']
    data['Lower_Band'] = data['SMA'] - std_prod * data['std']
    return data

def calculate_macd(prices_daily, short_period=12, long_period=26, signal_period=9):
    data = pd.DataFrame({'Close': prices_daily})
    data['ShortEMA'] = data['Close'].ewm(span=short_period).mean()
    data['LongEMA'] = data['Close'].ewm(span=long_period).mean()
    data['MACD_Line'] = data['ShortEMA'] - data['LongEMA']
    data['Signal_Line'] = data['MACD_Line'].ewm(span=signal_period).mean()
    data['Signal_Diff'] = data['Signal_Line'].diff()
    data['Signal_Acc'] = data['Signal_Line'].diff()
    data['MACD_Histogram'] = data['MACD_Line'] - data['Signal_Line']
    data['Hist_Diff'] = data['MACD_Histogram'].ewm(span=long_period).mean().diff()
    return data

def calculate_rsi(data, period=14):
    data = pd.DataFrame({'Close': data})
    data['PriceChange'] = data['Close'].diff()  # Calculate daily price changes
    data['Gain'] = data['PriceChange'].apply(lambda x: x if x > 0 else 0)  # Separate gains
    data['Loss'] = data['PriceChange'].apply(lambda x: -x if x < 0 else 0)  # Separate losses

    # Calculate average gain and average loss using rolling windows
    data['AverageGain'] = data['Gain'].rolling(window=period).mean()
    data['AverageLoss'] = data['Loss'].rolling(window=period).mean()

    # Calculate relative strength and RSI
    data['RS'] = data['AverageGain'] / data['AverageLoss']
    data['RSI'] = 100 - (100 / (1 + data['RS']))

    return list(data['RSI'])

def history_with_date(symbol, interval='day', span='year'):
    historicals = r.get_stock_historicals(symbol, interval, span)
    prices = [float(day_data['close_price']) for day_data in historicals]
    
    quote = r.get_stock_quote_by_symbol(symbol)
    if quote['last_non_reg_trade_price'] != None: # Non-Regular Hours
        prices.append(float(quote['last_non_reg_trade_price']))
    else:
        prices.append(float(quote['last_trade_price']))

    dates = [datetime.fromisoformat(day_data['begins_at']).astimezone(datetime.now().tzinfo) for day_data in historicals]
    if len(dates) < len(prices):
        dates.append(datetime.now())

    if interval == '10minute':
        dates = [date.strftime("%I:%M %p") for date in dates]
    elif interval == 'hour':
        dates = [date.strftime("%m/%d %I:%M %p") for date in dates]
    else:
        dates = [date.strftime("%m/%d/%Y") for date in dates]
    # highs = [float(day_data['high_price']) for day_data in historicals]
    # lows = [float(day_data['low_price']) for day_data in historicals]
    return prices, dates

def history(symbol, interval='day', span='year'):
    historicals = r.get_stock_historicals(symbol, interval, span)
    prices = [float(day_data['close_price']) for day_data in historicals]
    
    quote = r.get_stock_quote_by_symbol(symbol)
    if quote['last_non_reg_trade_price'] != None: # Non-Regular Hours
        prices.append(float(quote['last_non_reg_trade_price']))
    else:
        prices.append(float(quote['last_trade_price']))

    return prices

def high_low_history(symbol, interval='day', span='year'):
    historicals = r.get_stock_historicals(symbol, interval, span)
    highs = [float(day_data['high_price']) for day_data in historicals]
    lows = [float(day_data['low_price']) for day_data in historicals]
    prices = [float(day_data['close_price']) for day_data in historicals]

    return prices, highs, lows

def high_low_history_with_dates(symbol, interval='day', span='year'):
    historicals = r.get_stock_historicals(symbol, interval, span)
    highs = [float(day_data['high_price']) for day_data in historicals]
    lows = [float(day_data['low_price']) for day_data in historicals]
    prices = [float(day_data['close_price']) for day_data in historicals]

    dates = [datetime.fromisoformat(day_data['begins_at']).astimezone(datetime.now().tzinfo) for day_data in historicals]
    if len(dates) < len(prices):
        dates.append(datetime.now())

    if interval == '10minute':
        dates = [date.strftime("%I:%M %p") for date in dates]
    elif interval == 'hour':
        dates = [date.strftime("%m/%d %I:%M %p") for date in dates]
    else:
        dates = [date.strftime("%m/%d/%Y") for date in dates]

    return prices, highs, lows, dates

def determine_action(highs: list[float], lows: list[float], prices: list[float]):
    rsi = calculate_rsi(prices, PARAMS['RSI_PERIOD'])
    rsi = [(datapoint / 100) for datapoint in rsi]
    rsi_rescaled = 1 - rsi[-1]
    # rsi_vals = {1: rsi_rescaled, -1: -(1 - rsi_rescaled)}

    data = pd.DataFrame({'Highs':highs, 'Lows':lows, 'Prices':prices})
    
    high_bound = list(data['Highs'].rolling(PARAMS['MAC_WINDOW']).max())
    low_bound = list(data['Lows'].rolling(PARAMS['MAC_WINDOW']).min())
    
    rolling_average = list(data['Prices'].rolling(PARAMS['MAC_WINDOW']).mean())
    rolling_stddev = list(data['Prices'].rolling(PARAMS['MAC_WINDOW']).std())

    high_zscore = 0.99 * (high_bound[-2] - rolling_average[-2]) / rolling_stddev[-2]
    low_zscore = 1.01 * (low_bound[-2] - rolling_average[-2]) / rolling_stddev[-2]

    adjusted_high = (high_zscore * rolling_stddev[-2]) + rolling_average[-2]
    adjusted_low = (low_zscore * rolling_stddev[-2]) + rolling_average[-2]

    if lows[-1] > adjusted_high:
        return -(1 - rsi_rescaled)
    if highs[-1] < adjusted_low:
        return rsi_rescaled

    return 0

def interval_span_for_time(days: float) -> tuple[str, str]:
    if days <= 1:
        return '10minute', 'day'
    elif days <= 7:
        return 'hour', 'week'
    elif days <= 31:
        return 'day', 'month'
    elif days <= 31*3:
        return 'day', '3month'
    elif days <= 366:
        return 'day', 'year'
    else:
        return 'week', '5year'

def equity_graph():
    all_trades = r.get_all_positions()

    most_recent_trade = None
    for trade in all_trades:
        update = datetime.fromisoformat(trade['updated_at'])
        if most_recent_trade == None or most_recent_trade < update:
            most_recent_trade = update

    time_since_last_trade: timedelta = datetime.now(most_recent_trade.tzinfo) - most_recent_trade
    interval, span = interval_span_for_time(time_since_last_trade.days)

    current_holdings = r.build_holdings()

    values = []
    toplevel_dates = []
    for stock, buy_data in current_holdings.items():
        hist, dates = history_with_date(stock, interval, span)
        toplevel_dates = dates # Should be identical for all stock. Should.

        while len(hist) > len(values):
            values.append(0)
        for i, price in enumerate(hist):
            values[i] += price * float(buy_data['quantity'])
    
    profile = r.build_user_profile()
    for i in range(len(values)):
        values[i] += float(profile['cash'])

    return values, toplevel_dates

def holdings_data():
    return r.build_holdings() 

def current_total_value():
    profile = r.build_user_profile()
    return float(profile['equity']) + float(profile['cash'])
