# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:48:44 2024

@author: mszwagrzak
"""
import sys
import pickle
from pickle_loader import pickle_loader

# This script takes filepath as input and removes the empty tickers

def tech_clean(dataset):
    clean_dataset = dataset.copy()
    tickers = list(dataset.keys())
    removed_tickers = []
    
    for ticker in tickers:
        if len(dataset[ticker]) == 0: # Remove tickers that are empty 
            clean_dataset.pop(ticker, None)
            removed_tickers.append(ticker)
        else: # Remove tickers that don't contain the full dataset 
            first_time = dataset[ticker].index.to_pydatetime()[0].strftime('%d-%m-%Y')
            last_time = dataset[ticker].index.to_pydatetime()[-1].strftime('%d-%m-%Y')
            if first_time != '30-09-2021' or last_time != '29-09-2023':
                clean_dataset.pop(ticker, None)
                removed_tickers.append(ticker)
    
    return clean_dataset, removed_tickers 

filepath = sys.argv[1]
technical_data = pickle_loader(filepath)
clean_technical_data, _ = tech_clean(technical_data)

with open("clean_technical_data.pickle", 'wb') as f:
        pickle.dump(clean_technical_data, f)