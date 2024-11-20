#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Share value by ticker, required rate of return, and terminal growth rate variables
Created by grc 08.07.24

if __name__ == "__main__": for spot checking single companies from command line. argv[2] = cost of capital and argv[3] = terminal growth rate
Company class library (this file) for importing into other programs - also includes v1 functionality
"""

import requests
import pandas as pd
import yfinance as yf


class Company:
    def __init__(self, ticker, required_return_rate, term_growth_rate):
        self.ticker = ticker
        self.required_return_rate = required_return_rate / 100
        self.term_growth_rate = term_growth_rate / 100

    def get_historical_fcf(self):
        
        api_key = "1ca99c9386594620ee2d7eef421e6b17"
        url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{self.ticker}?apikey={api_key}"
        
        response = requests.get(url)
        data = response.json()

        free_cash_flow_data = []
        for item in data:
            free_cash_flow = item['freeCashFlow']
            date = item['date']
            free_cash_flow_data.append({'date': date, 'freeCashFlow': free_cash_flow})

        df = pd.DataFrame(free_cash_flow_data[::-1])
        print(f"\nHistorical FCFs:\n{df}")
        return df

    def calculate_avg_fcf_change(self, df):
        df['percent_change'] = df['freeCashFlow'].pct_change()
        avg_fcf_change = df['percent_change'].mean()
        fcf_percent_change = round(avg_fcf_change * 100, 1)
        print(f"\nAvg % FCF Change: {fcf_percent_change}%")
        return avg_fcf_change

    def forecast_future_fcfs(self, last_fcf_value, avg_fcf_change, df):
        num_future_periods = 10
        future_values = [last_fcf_value * (1 + avg_fcf_change) ** i for i in range(1, num_future_periods + 1)]
        future_dates = pd.date_range(start=pd.to_datetime(df['date'].iloc[-1]), periods=num_future_periods + 1, freq='YE')[1:]

        future_df = pd.DataFrame({
            'date': future_dates,
            'future_freeCashFlow': future_values,
            'discounted_future_value': self.calculate_discounted_future_values(future_values)
        })

        print(f"\nFuture Free Cash Flow Projections:\n{future_df}")
        return future_df

    def calculate_discounted_future_values(self, future_values):
        discounted_future_values = [future_value / (1 + self.required_return_rate) ** i for i, future_value in enumerate(future_values, start=1)]
        return discounted_future_values

    def calculate_terminal_value(self, last_future_fcf_value):
        terminal_value = (last_future_fcf_value * (1 + self.term_growth_rate)) / (self.required_return_rate - self.term_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + self.required_return_rate) ** (10 + 1))

        terminal_df = pd.DataFrame({
            'Terminal Value': [terminal_value],
            'Discounted Terminal Value': [discounted_terminal_value]
        })

        print(f"\nTerminal Value and Present Value:\n{terminal_df}")
        return discounted_terminal_value

    def calculate_present_value(self, discounted_future_values, discounted_terminal_value):
        present_value = sum(discounted_future_values) + discounted_terminal_value
        print(f"\nPresent Value:\n{present_value:.6e}")
        return present_value

    def get_net_debt(self):
        api_key = "1ca99c9386594620ee2d7eef421e6b17"
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{self.ticker}?apikey={api_key}"

        response = requests.get(url)
        data = response.json()

        most_recent = max(data, key=lambda x: x["date"])
        net_debt = most_recent.get("netDebt")
        print(f"\nNet Debt:\nValue:{net_debt:.6e}")
        return net_debt

    def calculate_equity_value(self, present_value, net_debt):
        equity_value = present_value - net_debt
        print(f"\nValue of Equity:\n{equity_value:.6e}")
        return equity_value

    def calculate_share_value(self, equity_value):
        implied_shares_outstanding = self.get_implied_shares_outstanding()
        if implied_shares_outstanding:
            print(f"\nImplied Shares Outstanding: {implied_shares_outstanding}")
            share_value = equity_value / implied_shares_outstanding
            print(f"\nShare Value:\n{share_value}")
            return share_value
        else:
            print("\nImplied Shares Outstanding data not found.")
            return None

    def get_implied_shares_outstanding(self):
        ticker_data = yf.Ticker(self.ticker)
        return ticker_data.info.get('impliedSharesOutstanding')

    def get_current_share_price(self):
        ticker_data = yf.Ticker(self.ticker)
        current_price = ticker_data.info.get("currentPrice")
        if current_price is not None:
            print(f"\nCurrent Share Price: {current_price}")
            return current_price
        else:
            print("\nCould not find the current share price.")
            return None

    def get_10yr_treasury_yield(self):
        api_key = "c13ac462a4d472cfb9f8766dab98c7aa"
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&file_type=json"

        response = requests.get(url)
        data = response.json()
        observations = data.get("observations", [])

        if observations:
            most_recent = max(observations, key=lambda x: x["date"])
            print(f"\nMost Recent 10YR Treasury Rate:\nValue: {most_recent.get('value')}")
            return most_recent.get('value')
        print("No observations found for 10YR Treasury Rate.")
        return None

    def run_analysis(self):
        # Step 1: Get Historical FCF
        df = self.get_historical_fcf()

        # Step 2: Calculate Average FCF Change
        avg_fcf_change = self.calculate_avg_fcf_change(df)

        # Step 3: Forecast Future FCFs
        last_fcf_value = df['freeCashFlow'].iloc[-1]
        future_df = self.forecast_future_fcfs(last_fcf_value, avg_fcf_change, df)

        # Step 4: Calculate Terminal Value
        discounted_terminal_value = self.calculate_terminal_value(future_df['future_freeCashFlow'].iloc[-1])

        # Step 5: Calculate Present Value
        present_value = self.calculate_present_value(future_df['discounted_future_value'], discounted_terminal_value)

        # Step 6: Get Net Debt
        net_debt = self.get_net_debt()

        # Step 7: Calculate Equity Value
        equity_value = self.calculate_equity_value(present_value, net_debt)

        # Step 8: Calculate Share Value
        self.calculate_share_value(equity_value)

        # Step 9: Get Current Share Price
        self.get_current_share_price()

        # Step 10: Get 10 Year Treasury Yield
        self.get_10yr_treasury_yield()


if __name__ == "__main__":
    import sys
    ticker = sys.argv[1]
    required_return_rate = float(sys.argv[2])
    term_growth_rate = float(sys.argv[3])

    company = Company(ticker, required_return_rate, term_growth_rate)
    company.run_analysis()
