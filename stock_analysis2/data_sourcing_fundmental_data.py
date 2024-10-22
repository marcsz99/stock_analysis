# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 17:02:47 2023

@author: marcs
"""

import pandas as pd
import time
import yfinance as yf
import pickle


SP500 = pd.read_csv(r"C:\Users\marcs\OneDrive\Documents\s&p_500.txt", sep='\t')
ticker_lst = list(SP500['Symbol'])


def get_stock_data_fundemental(ticker_lst, data_type):
    """
    

    Parameters
    ----------
    ticker_lst : str
        List of Stock Symbols
    data_type : str
        Data type function to use 

    Returns
    -------
    Dict of DF's for each ticker for chosen data_type 

    """
    
    data = {}
    for i, tick in enumerate(ticker_lst):
        ticker_class = yf.Ticker(tick)
        data_ticker = getattr(ticker_class, data_type)
        data[tick] = data_ticker
        time.sleep(5)
        print(i / len(ticker_lst), '% complete')
    
    with open("/Users/marcs/OneDrive/Documents/stock_analysis2/batch_2/" + data_type +  "_us.pickle", 'wb') as f:
        pickle.dump(data, f)
    
    return data 
 
#%% 
# testing 

test_data = get_stock_data_fundemental(ticker_lst[:2], 'quarterly_income_stmt')


#%%
# run for income statment 

income_statement = get_stock_data_fundemental(ticker_lst, 'quarterly_income_stmt')


#%%
# run for balence sheet

balence_sheet = get_stock_data_fundemental(ticker_lst, 'quarterly_balance_sheet')


#%%

cash_flow = get_stock_data_fundemental(ticker_lst, 'quarterly_cashflow')


