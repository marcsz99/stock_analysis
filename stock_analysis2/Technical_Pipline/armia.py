# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 16:36:31 2024

@author: mszwagrzak
"""

from pickle_loader import pickle_loader
import pandas as pd
import numpy as np
import pmdarima as pm
import pickle

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
        smoothing_data = self.smoothing_data
        
        predictions_dict = {}
        
        for stock, lst_models in trained_models.items():
            chunk_predictions = []
            lst_stock_data = smoothing_data[stock]
            
            for i, model in enumerate(lst_models):
                final_stock_value = lst_stock_data[i][-1]
                
                value_prediction, conf_int = model.predict(n_periods = num_forcast_periods, return_conf_int = True)
                value_prediction = value_prediction[-1]
                conf_int = conf_int[-1]
                
                chunk_predictions.append((chunk_end_dates[i], (value_prediction / final_stock_value, conf_int[1] / conf_int[0])))
            
            predictions_dict[stock] = chunk_predictions
        
        return predictions_dict
            
            
    
    
    def fit_ARMIA(self, smoothing_data):
        trained_models = {}
        
        i = 0
        
        for stock, smoothed_stock_data in smoothing_data.items():
            stock_models = []
            for i, smoothed_chunk in enumerate(smoothed_stock_data):
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
#preds_s20 = armia_obj.get_ARMIA_predictions(20)

#%%
pred_s20 = armia_obj.get_ARMIA_predictions(20)
pred_s30 = armia_obj.get_ARMIA_predictions(30)
pred_s40 = armia_obj.get_ARMIA_predictions(40)

all_pred = [pred_s20, pred_s30, pred_s40]

#%%


class get_final_dataset():
    
    
    def __init__(self, all_pred):
        self.all_pred = all_pred
        self.index = list(all_pred[0].keys())
        first_stock_predictions = all_pred[0][self.index[0]]
        self.timestamps = [prediction[0] for prediction in first_stock_predictions]
    
    def get_dataset(self):
        self.by_chunk = self.sort_by_chunk()
        self.dfs = self.create_dfs()
        return self.dfs
        
    def sort_by_chunk(self):
        timestamps = self.timestamps
        stocks = self.index
        all_pred = self.all_pred 
        
        sorted_dict = {timestamp : {stock : [] for stock in stocks } for timestamp in timestamps}
        
        for time_stamp, stock_dict in sorted_dict.items():
            for stock in stocks:
                for pred_dict in all_pred:
                    pred = pred_dict[stock]
                    for chunk_pred in pred:
                        if chunk_pred[0] == time_stamp:
                            stock_dict[stock].append(chunk_pred[1]) # to change after test
        
        return  sorted_dict
    
    def create_dfs(self):
        by_chunk = self.by_chunk
        final_dfs = {}
        
        for chunk, stock_data in by_chunk.items():
           
            num_tuples = len(next(iter(stock_data.values())))

            # Ensure all stocks have the same number of tuples
            if not all(len(v) == num_tuples for v in stock_data.values()):
                raise ValueError("All stock entries must contain the same number of tuples.")

            # Initialize dictionaries for price and cost columns
            prediction_columns = {}
            conf_columns = {}

            # Loop through the stock data and assign values to columns
            for idx in range(num_tuples):
                prediction_columns[f's{(idx + 2) * 10}p'] = [data[idx][0] for data in stock_data.values()]
                conf_columns[f's{(idx + 2) * 10}c'] = [data[idx][1] for data in stock_data.values()]            

            # Combine price and cost columns
            all_columns = {**prediction_columns, **conf_columns}

            # Create the DataFrame with the stock names as the index
            df = pd.DataFrame(all_columns, index=stock_data.keys())

            final_dfs[chunk] = df
                            
        return final_dfs
        
final_obj = get_final_dataset(all_pred)
final_dfs = final_obj.get_dataset()

        
#%%

with open("ARMIA_dfs.pickle", 'wb') as f:
        pickle.dump(final_dfs, f)
