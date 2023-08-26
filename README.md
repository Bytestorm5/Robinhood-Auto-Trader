# Robinhood Auto Trader
Automatically buys and sells stocks, using the `robin_stocks` library. Also includes a local web interface to allow for parameter tuning and monitoring.

# Quick Start
- Set up a virtual environment using `requirements.txt`
- Make a `.env` file by copying/renaming `default.env`, and enter your login information
- Run the dashboard with `flask --app flask_app run`
- Open the site and tune the algorithm as you see fit
- Schedule `execute_trades.py` to execute daily, either manually or automatically.
> Tip: You can use the `--auto` argument when running `execute_trades.py` to bypass confirmation messages for any order.

# Disclaimer
This git repository and the associated documentation is not, nor does it contain, financial advice. Before using the algorithm or any trading strategy, make sure you understand the risks involved.

The info here comes from my personal (more importantly, non-professional) experience developing this tool and is not professional advice. Nothing here is guaranteed to be accurate. 

Trading, including algorithmic trading, is risky. Only trade with money you can afford to lose. I'm not responsible for any losses you might incur using this algorithm.

Keep in mind that financial markets are unpredictable.

By using this algorithm, you accept that you're responsible for your actions. I'm not liable for any losses from using this tool.