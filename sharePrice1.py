#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Share value by ticker, required rate of return, and terminal growth rate variables
Created by grc 08.07.24

v1 (this file) for spot checking single companies from command line
v2 library for importing into other programs
"""

import requests
import pandas as pd
import sys
import yfinance as yf
from bs4 import BeautifulSoup

# sys.argv() User Entered Arguments

ticker = sys.argv[1]
requiredReturnRate = float(sys.argv[2]) / 100
termGrowthRate = float(sys.argv[3]) / 100

# Collect historical FCF for Command-Entered Ticker

api_key = "1ca99c9386594620ee2d7eef421e6b17" #retrieved from fmp account
url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={api_key}"

response = requests.get(url)
data = response.json()
  
# Create historical FCF data frame

free_cash_flow_data = []
for item in data:
  free_cash_flow = item['freeCashFlow']
  date = item['date']
  free_cash_flow_data.append({'date': date, 'freeCashFlow': free_cash_flow})

df = pd.DataFrame(free_cash_flow_data[::-1])
print(f"\nHistorical FCFs:\n{df}")

# Calculate average % change of historical FCFs

df['percent_change'] = df['freeCashFlow'].pct_change()
avgFCFChange = df['percent_change'].mean()
FCFPerCentChange = round(avgFCFChange * 100, 1)
print(f"\nAvg % FCF Change: {FCFPerCentChange}%")

# Print % FCF change by year to verify correct

# print(f"\n{df['percent_change']}")

# Forecast future FCFs

numFuturePeriods = 10
last_FCFvalue = df['freeCashFlow'].iloc[-1]
future_values = [last_FCFvalue * (1 + avgFCFChange) ** i for i in range(1, numFuturePeriods + 1)]
future_dates = pd.date_range(start=pd.to_datetime(df['date'].iloc[-1]), periods=numFuturePeriods + 1, freq='YE')[1:]

# Calculate discounted future values

discounted_future_values = [future_value / (1 + requiredReturnRate) ** i for i, future_value in enumerate(future_values, start=1)]

# Create FCF DataFrame

future_df = pd.DataFrame({
    'date': future_dates,
    'future_freeCashFlow': future_values,
    'discounted_future_value': discounted_future_values
})

print(f"\nFuture Free Cash Flow Projections:\n{future_df}")

# Calculate terminal value and discounted terminal value

last_future_FCFvalue = future_df['future_freeCashFlow'].iloc[-1]
#print("\n", last_future_FCFvalue) #for verification
termValue = (last_future_FCFvalue * (1 + termGrowthRate)) / (requiredReturnRate - termGrowthRate)
discounted_terminal_value = termValue / ((1 + requiredReturnRate) ** (numFuturePeriods + 1))

# Create Terminal Value DataFrame

terminal_df = pd.DataFrame({
    'Terminal Value': [termValue],
    'Discounted Terminal Value': [discounted_terminal_value]
})

print(f"\nTerminal Value and Present Value:\n{terminal_df}")

# PV = sum of discounted FCFs and Terminal Value

present_value = sum(discounted_future_values) + discounted_terminal_value
print(f"\nPresent Value:\n{present_value:.6e}")

# Collect net debt $ for Command-Entered Ticker

url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={api_key}"

response = requests.get(url)
data = response.json()

most_recent = max(data, key=lambda x: x["date"])
    
date = most_recent.get("date")
netDebt = most_recent.get("netDebt")
    
print(f"\nNet Debt:\nDate:{date}\nValue:{netDebt:.6e}")

# Value of Equity = PV - Net Debt

equityValue = present_value - netDebt

print(f"\nValue of Equity:\n{equityValue:.6e}")

# Collect and Print Diluted Shares Outstanding from yfinance

ticker_data = yf.Ticker(ticker)
implied_shares_outstanding = ticker_data.info.get('impliedSharesOutstanding')

if implied_shares_outstanding:
    print(f"\nImplied Shares Outstanding: {implied_shares_outstanding}")
    #print(ticker_data.info) #print entire .info dictionary for reference
else:
    print("\nImplied Shares Outstanding data not found.")

# Calculate and Print Share Value

shareValue = equityValue / implied_shares_outstanding
print(f"\nShare Value:\n{shareValue}")

# Collect and Print Current Share Price from Yahoo Finance Webpage

url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics/"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

fin_streamer = soup.find('fin-streamer', {'data-symbol': f'{ticker}', 'data-field': 'regularMarketPrice'})
if fin_streamer:
    data_value = fin_streamer['data-value']
    print(f"\nCurrent Share Price: {data_value}")
else:
    print("\nCould not find the data value.")

# Collect and Print Current 10 Year Treasury Yield for Reference

api_key = "c13ac462a4d472cfb9f8766dab98c7aa" #retrieved from Mark Funk FRED account
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&file_type=json"

response = requests.get(url)
data = response.json()
observations = data.get("observations", [])
    
if observations:
    # Find the most recent observation
    most_recent = max(observations, key=lambda x: x["date"])
        
    date = most_recent.get("date")
    value = most_recent.get("value")
    
    print(f"\nMost Recent 10YR Treasury Rate:\nDate: {date}\nValue: {value}")    
else:
    print("No observations found in the response.")