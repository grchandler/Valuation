import requests
from bs4 import BeautifulSoup

# URL of the S&P 500 companies list on Wikipedia
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing the S&P 500 companies
    table = soup.find('table', {'id': 'constituents'})

    # Initialize an empty dictionary for company names and tickers
    sp500_dict = {}

    # Iterate through the rows of the table
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) > 1:
            ticker = cells[0].text.strip()  # Ticker symbol
            company_name = cells[1].text.strip()  # Company name
            sp500_dict[company_name] = ticker

    # Print the resulting dictionary
    for company, ticker in sp500_dict.items():
        print(f"{company}: {ticker}")

else:
    print("Failed to retrieve data.")
