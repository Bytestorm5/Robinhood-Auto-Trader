from flask import Flask, render_template, send_from_directory, url_for, redirect, session, jsonify
from flask import request
import json
import os
import requests
from base64 import b64encode
import re
import robin_trader
import sim_trader
import pandas as pd
#from flask_limiter import Limiter

#import subprocess

#from flask_cors import CORS #comment this on deployment

# ENCRYPTION_KEY = ''
# if os.path.exists("secret.key"):
#     ENCRYPTION_KEY = open("secret.key", "rb").read()
# else:
#     ENCRYPTION_KEY = Fernet.generate_key()
#     with open("secret.key", "wb") as key_file:
#         key_file.write(ENCRYPTION_KEY)
# fernet = Fernet(ENCRYPTION_KEY)


app = Flask(__name__, static_folder='static')

@app.route("/")
def home():     
    return render_template("index.html")

@app.route("/api/equityGraph")
def equity_graph():
    values, dates = robin_trader.equity_graph()
    return jsonify(values=values, dates=dates)

@app.route("/api/getHoldings")
def get_holdings():
    holdings = robin_trader.holdings_data()
    reformatted_holdings = []
    for symbol, holding in holdings.items():
        new_hold = holding
        new_hold['symbol'] = symbol
        reformatted_holdings.append(new_hold)
    return jsonify(reformatted_holdings)


@app.route("/stock")
def stock():
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', 'day')
    span = request.args.get('span', 'year')

    values, highs, lows, labels = robin_trader.high_low_history_with_dates(symbol, interval, span)

    radii = [0] * len(values)
    bgs = ['blue'] * len(values)

    START = max(robin_trader.PARAMS['RSI_PERIOD'], robin_trader.PARAMS['MAC_WINDOW'], robin_trader.PARAMS['STDDEV_WINDOW'], robin_trader.PARAMS['MAC_VISION'], robin_trader.PARAMS['BOLLINGER_WINDOW'])

    if interval == 'day' and len(values) > 39:
        for i in range(START, len(values)):
            action = robin_trader.determine_action(highs[:i], lows[:i], values[:i])
            if action > 0:
                radii[i-1] = 2
                bgs[i-1] = 'green'
            elif action < 0:
                radii[i-1] = 2
                bgs[i-1] = 'red'
        
    # upper_band = list(robin_trader.calculate_bollinger(values, 20, 2)['Upper_Band'])
    # upper_band = [values[i] if i <= 39 else upper_band[i] for i in range(len(upper_band))]

    # lower_band = list(robin_trader.calculate_bollinger(values, 20, 2)['Lower_Band'])
    # lower_band = [values[i] if i <= 39 else lower_band[i] for i in range(len(lower_band))]

    data = pd.DataFrame({'Highs':highs, 'Lows':lows})
    
    if min(len(highs), len(lows)) < 10:
        return 0

    upper_band = values[:10] +  list(data['Highs'].rolling(10).mean())[10:]
    lower_band = values[:10] + list(data['Lows'].rolling(10).mean())[10:]

    return render_template("stock.html", values=str(values), lower_band=str(lower_band), upper_band=str(upper_band), labels=str(labels), radii=str(radii), bgs=str(bgs))

@app.route("/params", methods=['GET'])
def params(): 
    return render_template("params.html", PARAMS=robin_trader.PARAMS)

@app.route("/api/simTrade")
def sim_trade():
    start_value = request.args.get("start_value", robin_trader.current_total_value())
    values, cash, times = sim_trader.sim_trades(start_value)
    return jsonify(values=values, cash=cash, times=times)

@app.route("/api/setParams", methods=['POST'])
def set_params():
    keys = []
    with open('.env', 'r') as reader:
        lines = reader.readlines()
        for line in lines:
            keys.append(line.split('=')[0])
    with open('.env', 'w') as writer:
        writer.write(f"EMAIL=\"{os.environ.get('EMAIL')}\"\n")
        writer.write(f"PASSWORD=\"{os.environ.get('PASSWORD')}\"\n")
        writer.write(f"OTP_CODE=\"{os.environ.get('OTP_CODE')}\"\n")

        for field in [key for key in keys if key not in ['EMAIL', 'PASSWORD', 'OTP_CODE']]:
            value = request.form.get(field, os.environ.get(field))
            if value == None:
                print(f"{field} is None")
                # Don't touch it, it's probably broken
            else:
                if re.match(r'^\d+\.\d+$', value):
                    value = float(value)
                elif re.match(r'^\d+$', value):
                    value = int(value)

                writer.write(f"{field}=\"{value}\"\n")
                os.environ[field] = str(value)
                robin_trader.PARAMS[field] = value

    return redirect(url_for('params'))

@app.route("/stockPool")
def stock_pool():
    data = ""
    for symbol in robin_trader.PARAMS['STOCK_POOL'].split():
        row = "<tr {hsl_vals}>"
        row += f"<td class=\"td-symbol\"><a href=\"{url_for('stock')}?symbol={symbol}\">{symbol}</a></td>"

        hist, highs, lows = robin_trader.high_low_history(symbol)
        action = robin_trader.determine_action(highs, lows, hist)

        row += f"<td class=\"td-number\">${hist[-1]}</td>"
        if action < 0:
            percentage = (action*-1)*100
            row += "<td class=\"td-number\">Sell</td>"
            row += f"<td class=\"td-number\">{int(percentage*10)/10}%</td>"            
            row = row.format(hsl_vals=f"style=\"background-color: hsl(0, {int(percentage)}%, {100-int(percentage)//2}%);\"")
        elif action > 0:
            percentage = (action)*100
            row += "<td class=\"td-number\">Buy</td>"
            row += f"<td class=\"td-number\">{int(percentage*10)/10}%</td>"            
            row = row.format(hsl_vals=f"style=\"background-color: hsl(130, {int(percentage)}%, {100-int(percentage)//2}%);\"")
        else:
            percentage = "N/A"
            row += "<td class=\"td-number\">Hold</td>"
            row += f"<td class=\"td-number\">N/A</td>"
            row = row.format(hsl_vals=f"")
        row += "</tr>"
        data += row

    return render_template("pool.html", table_data=data)

if __name__ == '__main__':    
    #pgcr_thread = subprocess.run(['python', 'PGCRscanner.py'], capture_output=True, text=True, check=True)
    #CORS(app) #comment this on deployment
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    #pgcr_thread.terminate()
