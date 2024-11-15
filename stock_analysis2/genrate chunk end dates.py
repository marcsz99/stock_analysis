# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 16:08:48 2024

@author: mszwagrzak
"""
from pickle_loader import pickle_loader
import pickle

fundamental_data = pickle_loader("final_fundamental_dict.pickle")
chunk_end_dates = list(fundamental_data['AOS'].columns)

with open("chunk_end_dates.pickle", 'wb') as f:
        pickle.dump(chunk_end_dates, f)

