# Algo Parameters
The following are parameters that would be entered in the `.env` file located at the root directory. All can be edited from the website except for the login.

## Robinhood Login
```
EMAIL=...
PASSWORD=...
OTP_CODE=...
```

Email and Password are self explanatory- you can get the OTP Code using [this](https://www.youtube.com/watch?v=C5buU4zjjx0) tutorial. It's not too complicated to do, just make sure to also enter the OTP code into your authenticator app so that you can still login yourself.

## RSI Period
```
RSI_PERIOD="8"
```

The RSI Period is used to weight how much of a stock to buy when a buy signal is received. When the RSI is high, less stock is bought, and when the RSI is low, more is bought. This helps mitigate cases where the algorithm picks a high point to buy on. It's reccomended to keep the RSI Period relatively small.

## Entry MACD
```
ENTRY_MACD_SHORT_PERIOD="12"
ENTRY_MACD_LONG_PERIOD="26"
ENTRY_MACD_SIGNAL_PERIOD="9"
```

The Entry MACD is used to determine when to buy a stock, and should generally be smaller than the Exit MACD so that it picks up on stock movements quicker. 

## Exit MACD
```
EXIT_MACD_SHORT_PERIOD="15"
EXIT_MACD_LONG_PERIOD="39"
EXIT_MACD_SIGNAL_PERIOD="9"
```

The Exit MACD is used to determine when to sell a stock, and should generally be larger than the Entry MACD so that it picks up on more long term stock movements.

## Min Funds
```
MIN_FUNDS="50"
```

This defines the minimum amount of funds that need to be in the account for the algorithm to be able to actually buy a stock. Despite the name this doesn't mean that the account will always have >$50 in it, but rather this prevents the algorithm from making extremely small buys.

## Sale Bounds
```
MAX_SELL_PROPORTION="1"
MAX_PROFIT_RATIO="1.5"
MIN_PROFIT_RATIO="1.2"
```

`MAX_SELL_PROPORTION` determines how much of a given stock should be sold when a sell signal is received. This should stay at 1.0 as returns per sale may vary otherwise. However you have the option to change that if you want.

`MAX_PROFIT_RATIO` defines the point at which the algorithm will take the profits it has and sell, regardless of whether a sell signal was generated otherwise. Generally you will want to lower this if the stocks you have picked are volatile, as the algorithm is less likely to pick up sudden spikes.

`MIN_PROFIT_RATIO` defines the minimum profit that must be observed before the algorithm can sell a stock. You will generally want to increase this with more volatile stocks to prevent suboptimal sales.

## Stock Pool
```
STOCK_POOL="NVDA AMD TSM GOOG MSFT"
```

The Stock Pool defines the stocks that the algorithm will actively trade. There is a tradeoff between returns and stability to keep in mind when deciding. 

Fewer stocks will generally yield higher returns but tends to be more risky, while having a broad range of stocks will give you some stability at the cost of lower overall returns.

Be wary of simply picking stocks that had the best performance in the past year- that performance isn't guaranteed to continue, especially so if that performance manifests as a large spike in price rather than a gradual one.