import pandas as pd
import numpy as np
import xlsxwriter
import requests
import math
from files.api_key import IEX_CLOUD_API_TOKEN

# Accept the value of your port5folio and output excel sheet saying how many shares of each S&P 500 company
# you should purchase toget an equal-weight version of the index fund

# The S&P 500 weighs how many shares of each company it has by the company's market cap in this case we are going
# to weight each company equally instead of weighting the bigger companies higher than the smaller ones

stocks = pd.read_csv('files/sp_500_stocks.csv')
cols = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
buy_sheet = pd.DataFrame(columns=cols)

#batch api calls to reduce ticker lookup time

# IEX Cloud limits batch api calls to 100 at a time so we need to split the ticker list into sublists of length 100
# The chunks function will make a list containing lists that contain 100 tickers

def chunks(lst, n):
    for i in range(0,len(lst), n):
        yield lst[i:i+n]

batch_symbol = list(chunks(stocks['Ticker'], 100))
batch_string = []
for i in range(len(batch_symbol)):
    batch_string.append(','.join(batch_symbol[i]))

#create a blank dataframe with columns cols
batch_df = pd.DataFrame(columns = cols)

for string in batch_string:
    # use & instead of ? for batch calls eg "quote&token" not "quote?token"
    batch_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?symbols={string}&types=quote&token={IEX_CLOUD_API_TOKEN}"
    batch_data = requests.get(batch_url).json()
    for symbol in string.split(','): #undo the join(',') for each sub list so we can have an interable list again
        price = batch_data[symbol]['quote']['latestPrice'] #parsing batch data require ticker, endpoint, key
        m_cap = batch_data[symbol]['quote']['marketCap']
        buy_sheet = buy_sheet.append(pd.Series([symbol, price, m_cap, 'N/A'], index=cols), ignore_index=True)


personal_capital = input("Enter the value of your available funds: ")
print(personal_capital)

# Check to make sure the input is a float if not we will catch the error and reprompt the user for a float
# We only want to handle value errors which is the error thrown when type casting a string to float
try:
    personal_capital = float(personal_capital)
except ValueError:
    print("Available funds must be an number\n")
    personal_capital = float(input("Enter the value of your available funds: "))

    # note if the user enters two non numbers twice it breaks I dont see why they would though thats probably their fault
