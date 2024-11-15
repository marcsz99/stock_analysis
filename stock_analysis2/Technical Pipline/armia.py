# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:36:31 2024

@author: mszwagrzak
"""

from pickle_loader import pickle_loader
import pandas as pd
import numpy as np
import pmdarima as pm

technical_data = pickle_loader("clean_technical_data.pickle")
chunk_end_dates = pickle_loader("chunk_end_dates.pickle")

class get_ARMIA_predictions():
    
    def __init__(self, dataset, chunk_end_dates):
        self.dataset = dataset
        self.chunk_end_dates = [date.tz_localize('America/New_York') for date in chunk_end_dates]
        self.chunked_data = self.get_12_month_chunks()
    
    def get_12_month_chunks(self):
        chunk_end_dates = self.chunk_end_dates
        dataset = self.dataset
        start_end_dates = []
        
        for date in chunk_end_dates:
            start_end_dates.append((date - pd.DateOffset(months=12), date))
        
        
        chunked_data_dict = {}
        for stock, data in dataset.items():
            chunked_data_stock = []
            
            for start_date, end_date in start_end_dates:
                full_data_chunked = data[(data.index >= start_date) & (data.index <= end_date)]
                chunked_data_stock.append(full_data_chunked['Close'].to_numpy())
        
            chunked_data_dict[stock] = chunked_data_stock
        
        return chunked_data_dict
    
    def get_ARMIA_predictions(self, len_smoothing_period):
        self.len_smoothing_period = len_smoothing_period
        
        self.smoothing_data = self.get_smoothing_data(len_smoothing_period)
        self.trained_models = self.fit_ARMIA(self.smoothing_data)
        self.num_forcast_periods = int(np.round(90/len_smoothing_period)) # 90 as prediction is 3 months ahead
        self.predictions_dict = self.forcast_models()
        
        return self.predictions_dict
    
    def forcast_models(self):
        trained_models = self.trained_models
        num_forcast_periods = self.num_forcast_periods
        chunk_end_dates = self.chunk_end_dates
        
        predictions_dict = {}
        
        for stock, lst_models in trained_models.items():
            chunk_predictions = []
            
            for i, model in enumerate(lst_models):
                fc, conf_int = model.predict(n_periods = num_forcast_periods, return_conf_int = True)
                chunk_predictions.append((chunk_end_dates[i], (fc, conf_int)))
            
            predictions_dict[stock] = chunk_predictions
        
        return predictions_dict
            
            
    
    
    def fit_ARMIA(self, smoothing_data):
        trained_models = {}
        
        for stock, smoothed_stock_data in smoothing_data.items():
            stock_models = []
            
            for smoothed_chunk in smoothed_stock_data:
                stock_models.append(\
                       pm.auto_arima(smoothed_chunk, d=1, seasonal=False, stepwise=True,\
                       suppress_warnings=True, error_action="ignore", max_p=6,\
                       max_order=None, trace=False))
            
            trained_models[stock] = stock_models
            
        return trained_models
        
        
    
    def get_smoothing_data(self, length):
        chunked_data = self.chunked_data
        smoothing_data = {}
        
        for stock, data in chunked_data.items():
            smoothed_stock_data = []
            
            for chunk in data:
                len_stock_set = chunk.size
                factor_missing_days = len_stock_set / 365 # factor which captures the ratio of missing days in the total number of days in the train set
                adjusted_smoothing_period = int(np.round(length * factor_missing_days)) # smoothing period ajusted for the missing days
                remainder = len_stock_set % adjusted_smoothing_period
                len_start_period = adjusted_smoothing_period + remainder
        
                first_value = np.mean(chunk[:len_start_period])
                other_values = np.mean(chunk[len_start_period:].reshape(-1, adjusted_smoothing_period), axis = 1)
                
                smoothed_stock_data.append(np.insert(other_values, 0, first_value))
            
            smoothing_data[stock] = smoothed_stock_data
        
        return smoothing_data


armia_obj = get_ARMIA_predictions(dataset = technical_data, chunk_end_dates = chunk_end_dates, )
preds_s20 = armia_obj.get_ARMIA_predictions(20)       
        