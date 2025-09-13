import yfinance as yf
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

def validate_date_format(date_text):
    # this ensures that the provided date is of the form xxxx-xx-xx
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_text):
        print(f"Warning: '{date_text}' is not of the form YYYY-MM-DD as requested. The program will continue regardless, but it might not work.")
    return date_text

if __name__ == "__main__":

    while True:
        tickers = input("Enter official stock codes (tickers) separated by spaces (eg. AAPL MSFT TSLA; Google a company if unsure) and press Enter: ").upper().split()
        startdate = validate_date_format(input("Enter the start of the date range you wish to consider in YYYY-MM-DD format (eg. 2022-01-01 for January 1st, 2022) and press Enter: "))
        enddate = validate_date_format(input("Enter the end of the date range you wish to consider in YYYY-MM-DD format, and press enter: "))

        # downloading data; the second line is to keep the tickers in the order that the user provides them
        data = yf.download(tickers, start=startdate, end=enddate, auto_adjust=True)["Close"]
        data = data[tickers]
        returns = data.pct_change().dropna()

        while True:

            showdata = input("Would you like to see prices per share at close of market and percentage changes (versus the previous day) for each stock? (yes/no, then press Enter): ").strip().lower()

            if showdata in ['yes', 'no']:
                break  # valid input; exit the asking loop
            print("Please answer with 'yes' or 'no'.")
        
        if showdata == 'yes':
            
            print("\nPrice in USD per share at close of market:")
            print(data.head(5))
            print("...")
            print(data.tail(5))
            # calculating daily returns
            returns_percent = (returns * 100).round(2).map(lambda x: f"{x:+.2f}%")
            print("\nPercentage change in price versus the previous day:")
            print(returns_percent.head(5))
            print("...")
            print(returns_percent.tail(5))
            print("Please note: skipped days were likely weekends or holidays.\n")

        # asking the user for weights for each stock in portfolio. Code will not break if the weights do not sum to 1
        weights = []
        print("\nNow we will consider the impacts of given stock weights on the portfolio's performance over the given time period.")
        for ticker in tickers:
            while True:
                try:
                    w = float(input(f"What weight would you like to consider for {ticker}? Input a decimal between 0 and 1 inclusive, and press Enter. "))
                    if 0 <= w <= 1:
                        weights.append(w)
                        break
                    else:
                        print("Weight must be between 0 and 1.")
                except ValueError:
                    print("Please enter a valid decimal number.")

        # normalize weights if they don't sum to 1 to prevent issues (why would you input weights like this?)
        weights = np.array(weights)
        if not np.isclose(weights.sum(), 1):
            weights = weights / weights.sum()
            print(f"Weights normalized to sum to 1: {dict(zip(tickers, weights.round(2)))}")
        # portfolio metrics
        dailyreturns = returns  # to retain numeric values
        
        # compunded annual returns
        tradingdays = len(dailyreturns)
        startprices = data.iloc[0].values
        endprices = data.iloc[-1].values

        annualizedreturns = ((endprices / startprices) ** (252 / tradingdays)) - 1
        
        # portfolio daily return metrics
        portfolioreturns = dailyreturns @ weights
        # finding annualised metrics
        portfolioannualreturn = ((1 + portfolioreturns).prod() ** (252 / tradingdays)) - 1
        portfoliovolatility = portfolioreturns.std() * np.sqrt(252)
        sharperatio = (portfolioannualreturn - 0.02) / portfoliovolatility

        print(f"\nPortfolio annual return: {portfolioannualreturn:.2%}")
        print(f"Portfolio annual volatility: {portfoliovolatility:.2%}")
        print(f"Portfolio Sharpe ratio (assuming 2% risk-free rate): {sharperatio:.2f}")
        for ticker, annualisedrets in zip(tickers, annualizedreturns):
            print(f"Annualized return for {ticker}: {annualisedrets:.2%}")

        # finding cumulative returns of each stock
        cumulativereturnsperstock = (1 + dailyreturns).cumprod()

        # finding cumulative returns of entire portfolio
        portfoliocumulativereturns = (1 + portfolioreturns).cumprod()

        # show the cumulative returns of the portfolio as well as each individual stock, one by one (one comparison graph per stock)
        plt.figure(figsize=(12,6))
        for ticker in tickers:
            plt.plot(cumulativereturnsperstock.index, cumulativereturnsperstock[ticker], label=f"{ticker} cumulative returns")

            plt.plot(portfoliocumulativereturns.index, portfoliocumulativereturns, label="Portfolio cumulative returns", linewidth=2, color="black")
            plt.title("Cumulative Returns")
            plt.xlabel("Date")
            plt.ylabel("Value multiplier of every USD invested / dimensionless")
            plt.legend()
            plt.grid(True)
            plt.show()

        while True:

            montecarlosims = input("Would you like to consider Monte Carlo simulations for this portfolio to determine what the most profitable weight for each stock would have been? (yes/no, then press Enter): ").strip().lower()

            if montecarlosims in ['yes', 'no']:
                break  # valid input; exit the asking loop
            print("Please answer with 'yes' or 'no'.")
        
        if montecarlosims == 'yes':

            np.random.seed()
            numberofportfoliostoconsider = int(input("Give the number of portfolios you would like to simulate. A number between 5,000 and 20,000 is typical; the higher the number goes, the smoother the frontier will be, but it can start to take absolutely ages to complete. Press Enter after writing your number: "))
            montecarloresults = np.zeros((3, numberofportfoliostoconsider)) #a matrix filled with zeroes; 3 rows and a column for each portfolio being run in the simulation
            #3 rows as we must consider the annual return, annual volatility and Sharpe ratio for each simulation
            allweights = np.zeros((len(tickers), numberofportfoliostoconsider))
            for k in range(numberofportfoliostoconsider):
                montecarloweights = np.random.random(len(tickers))
                montecarlonormalisedweights = montecarloweights/np.sum(montecarloweights) #now we have normalised weights for every ticker being considered
                allweights[:, k] = montecarlonormalisedweights
                # portfolio return & volatility
                montecarloportfolioreturn = ((1 + (returns @ montecarloweights)).prod() ** (252 / tradingdays)) - 1
                montecarloportfoliovolatility = (returns @ montecarloweights).std() * np.sqrt(252)
                montecarlosharperatio = (montecarloportfolioreturn - 0.02) / montecarloportfoliovolatility

                # storing results ([:,k] uses ALL rows and the kth column
                montecarloresults[:, k] = [montecarloportfolioreturn, montecarloportfoliovolatility, montecarlosharperatio]
                bestindex = np.argmax(montecarloresults[2, :])
                bestreturn, bestvolatility, bestsharperatio = montecarloresults[:, bestindex]
                bestweights = allweights[:, bestindex]
                
            #show the frontier plot, with the portfolio with the best Sharpe ratio shown with a red star and a legend
            plt.figure(figsize=(10,6))
            plt.scatter(
            montecarloresults[1, :],  # volatility
            montecarloresults[0, :],  # returns
            c=montecarloresults[2, :],  # Sharpe ratio
            cmap='viridis',
            alpha=0.7)
            plt.colorbar(label='Sharpe ratio')
            plt.scatter(bestvolatility, bestreturn, color='red', marker='*', s=200, label='Optimal portfolio!')
            plt.xlabel('Annual volatility')
            plt.ylabel('Annual return')
            plt.title('Monte Carlo Portfolio Simulation')
            plt.legend()
            plt.grid(True)
            plt.show()
        print("\nOptimal portfolio weights based on Monte Carlo simulation:")
        for ticker, weight in zip(tickers, bestweights):
            print(f"{ticker}: {weight:.2%}")

        # also print expected metrics
        print(f"\nExpected annual return: {bestreturn:.2%}")
        print(f"Expected annual volatility: {bestvolatility:.2%}")
        print(f"Sharpe ratio: {bestsharperatio:.2f}")


        # does the user wish to go again?
        while True:
            another = input("Would you like to go again with another set of tickers? (yes/no, then press Enter): ").strip().lower()
            if another in ['yes', 'no']:
                break
            print("Please answer with 'yes' or 'no'.")
        
        if another == 'no':
            print("Thank you, I hope you enjoyed this work - Eren Ozaydin :)")
            break
    #preventing unsightly abrupt closure of the program
    input("\nPress Enter now to exit the program.")

