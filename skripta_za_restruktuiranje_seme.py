import pandas as pd
import numpy as np

sp500_stocks = pd.read_csv('sp500_stocks.csv')
sp500_companies = pd.read_csv('sp500_companies.csv')
sp500_index = pd.read_csv('sp500_index.csv') 

# Brisanje null vrednosti
print(sp500_stocks.shape)

sp500_stocks.dropna(subset=['Close'], inplace=True)

print(sp500_stocks.shape)

# Dodavanje polja od interesa u stocks
merged_stocks = pd.merge(sp500_stocks, sp500_companies[['Symbol', 'Shortname', 'Marketcap']], on='Symbol', how='inner')

print(sp500_stocks.shape)

print(merged_stocks.head(1))

# Dodavanje vrednosti indeksa u stocks
merged_stocks = pd.merge(merged_stocks, sp500_index, on='Date', how='left')
merged_stocks.rename(
    columns= {
        'S&P500' : 'indexValue', 
        'Date' : 'date',
        'Symbol' : 'symbol',
        'Adj Close': 'adjClose',
        'Close': 'close',
        'High': 'high',
        'Low': 'low',
        'Open': 'open',
        'Volume': 'volume',
        'Shortname': 'shortname',
        'Marketcap': 'marketcap'
        }, 
        inplace=True)

# Tip kolona
print(merged_stocks.dtypes)

# Promena tipa kolona
merged_stocks['date'] = pd.to_datetime(merged_stocks['date'])

# Provera postojanja nedostajucih vrednosti u merged_stocks (nema, kao sto je i ocekivano)
filtered_stocks = merged_stocks[merged_stocks['date'] >= '2014-05-27']
nulls_in_indexValue = filtered_stocks['indexValue'].isnull()
null_count = nulls_in_indexValue.sum()
print(f"There are {null_count} null values in the 'indexValue' column.")


# Pravljenje kolekcije companies_stock_stats

# Pronalazak allTimeHigh-a i allTimeLow-a
agg_stats = merged_stocks.groupby('symbol')['adjClose'].agg(allTimeHigh = 'max', allTimeLow = 'min')
print(agg_stats)

sp500_companies.rename(columns={
       'Symbol': 'symbol',
       'Sector': 'sector',
       'State': 'state'
    }, inplace=True)

sp500_stocks.rename(columns={
       'Symbol': 'symbol',
       'Date': 'date',
       'Adj Close': 'adjClose',
       'Close': 'close',
       'High': 'high',
       'Low': 'low',
       'Open': 'open',
       'Volume': 'volume'
    }, inplace=True)

companies_stock_stats = pd.merge(sp500_companies[['symbol', 'sector', 'state']], agg_stats, on='symbol', how='inner')
companies_stock_stats['currentDate'] = '2024-05-24'

# Izracunavanje listingDate-a
listingDates = sp500_stocks.groupby('symbol')['date'].min().reset_index()
listingDates.rename(columns={'date': 'listingDate'}, inplace=True)
companies_stock_stats = pd.merge(companies_stock_stats, listingDates, on ='symbol', how='inner')
print(companies_stock_stats)

# Izracunavanje listingAdjustedClose-a
sorted_stocks = sp500_stocks.sort_values(by=['symbol', 'date'])
listingAdjustedClose = sorted_stocks.groupby('symbol').first().reset_index()
companies_stock_stats = pd.merge(companies_stock_stats, listingAdjustedClose[['symbol', 'adjClose']], on='symbol', how='inner')
companies_stock_stats.rename(columns={"adjClose": 'listingAdjustedClose'}, inplace=True)

# Izracunavanje currentAdjustedClose-a
currentAdjustedClose = sorted_stocks.groupby('symbol').last().reset_index()
companies_stock_stats = pd.merge(companies_stock_stats, currentAdjustedClose[['symbol', 'adjClose']], on='symbol', how='inner')
companies_stock_stats.rename(columns={"adjClose": 'currentAdjustedClose'}, inplace=True)

# Promena tipa kolona
# companies_stock_stats['currentDate'] = pd.to_datetime(companies_stock_stats['currentDate'])
# companies_stock_stats['listingDate'] = pd.to_datetime(companies_stock_stats['listingDate'])

# Tip kolona
print(companies_stock_stats.dtypes)

# Provera
print(companies_stock_stats[companies_stock_stats['symbol'] == 'MSFT'])
print(merged_stocks)

# Export companies_stock_stats to CSV
companies_stock_stats.to_csv('companies_stock_stats.csv', index=False)
merged_stocks.to_csv('merged_stocks.csv', index=False)