# yfinance-interactive-portfolio-simulator
An interactive Python tool that allows users to:
- retrieve historical stock prices and daily percentage changes;
- compute portfolio metrics: annual return, volatility, and Sharpe ratio;
- visualize (via plots) cumulative returns for individual stocks and the portfolio; and
- perform Monte Carlo simulations to find the portfolio weights that maximize the Sharpe ratio.

INPUT: 
- stock tickers
- start date
- end date
- weights of each stock in the portfolio
- number of Monte Carlo simulations you wish to perform

AVAILABLE OUTPUTS (the script asks if you want some of them):
- USD price data at close of market for both the first and last five days of the date range given
- percentage change data for these days (versus the previous day)
- portfolio annual return
- portfolio annual volatility
- portfolio sharpe ratio (assuming 2% risk-free rate)
- annualized return for each stock
- cumulative return graphs (one per stock, comparing the cumulative return of the stock with the portfolio's cumulative return)
- optimal portfolio weights based on Monte Carlo simulation
- Monte Carlo frontier plots (with the most optimal weight combination shown with a red star)
- expected annual return for most optimal portfolio (found by Monte Carlo simulations)
- expected annual volatility for most optimal portfolio (found by Monte Carlo simulations)
- Sharpe ratio for most optimal portfolio (found by Monte Carlo simulations)

NB the risk-free rate is hard coded at 2% but this can trivially be adjusted to a variable which the user inputs if you wish.

YOU WILL NEED:
- yfinance, pandas, numpy, re, matplotlib.pyplot

You can install them via pip:

pip install yfinance pandas numpy matplotlib


