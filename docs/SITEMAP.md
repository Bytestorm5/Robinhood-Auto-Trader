# Sitemap
This file contains details on each page of the website.

## Homepage
The homepage is nothing too complicated. It contains a graph showing the value of your assets over time, from the most recent trade onward. Below it is a table of all stocks held in the current account. You can click on any stock to see that stock's graph with some other metrics.

## Individual Stock Page
The stock page has three different graphs, in order:
- Stock Price
- Entry MACD
- Exit MACD

On each graph Buys and Sells are indicated with green and red dots respectively. 

You can use the following URL parameters to change the data being viewed:
- Symbol: Change the stock/etf being viewed
- Interval: Change the interval for data (reccomended to stick with 'day' as that's what the algo uses). Must be one of the following: `'5minute', '10minute', 'hour', 'day', 'week'`
- Span: Change the time range of the data (default 3 months, other reasonable options are '5year', 'year', and 'month'). Must be one of the following: `'day', 'week', 'month', '3month', 'year', '5year'`

## Stock Pool Page
The stock pool page shows every symbol that algorithm is actively trading on, as well as its current position on the stock. While these should match the actual actions of the bot, it is not a guarantee. This is because it is *possible*, though unlikely, that the fluctuations of the stock during the day could change the bot's position. However this is almost exclusively in cases where the bot is very close to buyinng or selling anyway.

You can also click on any symbol here to go to its individual stock page.

## Parameters
The Parameters page lets you change parameters and then immediately test them on the past year's data. See [PARAMS.md](PARAMS.md) for details on the different parameters and what they mean.

Important note, the ROI of the algorithm over the past year isn't guaranteed or even necessarily likely to hold for the next year. You should only use the ROI metrics in comparison to other configurations. 

For example, if a specific configuration has 150% returns, that doesn't necessarily mean that it will produce 150% returns over the next year. However it *does* mean that it is likely to produce higher returns in the next year compared to a configuration that has 140% returns over the last year.