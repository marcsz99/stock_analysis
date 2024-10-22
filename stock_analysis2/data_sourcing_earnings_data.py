#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 12:52:34 2023

@author: marcs
"""

import pandas as pd
import time
import yfinance as yf
import pickle

SP500 = pd.read_csv("/Users/marcs/OneDrive/Documents/s&p_500.txt", sep='\t')
ticker_lst = list(SP500['Symbol'])

def get_earnings_date(ticker_lst):
    """
    

    Parameters
    ----------
    ticker_lst : lst
        List of Stock Symbols

    Returns
    -------
    Dict of Dfs of earnings dates for every ticker 

    """
    
    data = {}
    
    for i, tick in enumerate(ticker_lst):
        ticker_class = yf.Ticker(tick)
        ticker_earn = ticker_class.earnings_dates
        data[tick] = ticker_earn
        time.sleep(5)
        print(i / len(ticker_lst), '% complete')
    
    with open("/Users/marcs/OneDrive/Documents/stock_analysis2/earnings_us.pickle", 'wb') as f:
        pickle.dump(data, f)
    
    return data 

#%%

earn_data = get_earnings_date(ticker_lst)