# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 19:05:40 2023

@author: marcs
"""

## intial train/test dataset : '2023-09-30' - '2022-06-30'

import pandas as pd
import time
import yfinance as yf
import pickle

SP500 = pd.read_csv(r"C:\Users\marcs\OneDrive\Documents\s&p_500.txt", sep='\t')
ticker_lst = list(SP500['Symbol'])


def get_stock_data_technical(ticker_lst, start, end):
    """
    

    Parameters
    ----------
    ticker_lst : lst
        List of Stock Symbols
    start: str
        Start date 
    end: str
        End date
    
    Returns
    -------
    Dict of DF's for each ticker for chosen data_type 

    """
    
    data = {}
    for i, tick in enumerate(ticker_lst):
        ticker_class = yf.Ticker(tick)
        data_ticker = ticker_class.history(start=start, end=end, period = '1d')
        data[tick] = data_ticker
        time.sleep(5)
        print(i / len(ticker_lst), '% complete')
    
    with open("/Users/marcs/OneDrive/Documents/stock_analysis2/technical_us.pickle", 'wb') as f:
        pickle.dump(data, f)
    
    return data 
 
#%%

technical_data = get_stock_data_technical(ticker_lst, '2021-09-30', '2023-09-30')    
