#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates dictionary of SP500 companies and tickers and iterates over each ticker to run the sharePrice2.py analysis.
This format can be used to iterate over any index of companies
Returns many lines depending on size of index - uses sys to write output to .txt file
Created by grc 08.07.24
"""

import requests
from bs4 import BeautifulSoup
import sharePrice2
import sys

sys.stdout = open("{__file__} output", "w")

# URL of the S&P 500 companies list (Wikipedia)
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing the S&P 500 companies
    table = soup.find('table', {'id': 'constituents'})

    # Initialize an empty dictionary
    sp500_dict = {}

    # Iterate through the rows of the table
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) > 1:
            ticker = cells[0].text.strip()  # Ticker symbol
            company_name = cells[1].text.strip()  # Company name
            sp500_dict[company_name] = ticker

    # Print the resulting dictionary (optional)
    print(sp500_dict)

    # Default values for required return rate and terminal growth rate
    required_return_rate = 10  # 10%
    term_growth_rate = 4  # 4%

    # Iterate over each ticker and run the analysis from sharePrice2.py
    for company, ticker in sp500_dict.items():
        print(f"\nAnalyzing {company} ({ticker})...")
        try:
            # Create a Company instance and run the analysis
            company_analysis = sharePrice2.Company(ticker, required_return_rate, term_growth_rate)
            company_analysis.run_analysis()
        except Exception as e:
            print(f"Error analyzing {company} ({ticker}): {e}")

else:
    print("Failed to retrieve the data. Status code:", response.status_code)
    
sys.stdout.close()