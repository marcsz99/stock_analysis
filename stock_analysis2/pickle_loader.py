# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 18:42:20 2023

@author: marcs
"""

# Pickle serializes a single object at a time, and reads back a single object - the pickled data is recorded in sequence on the file.

# If you simply do pickle.load you should be reading the first object serialized into the file (not the last one as you've written).

# After unserializing the first object, the file-pointer is at the beggining of the next object - if you simply call pickle.load again, it will read that next object - do that until the end of the file.

import pickle 

def pickle_loader(file_path):
    
    objects = []
    with (open(file_path, "rb")) as openfile:
        while True:
            try:
                objects.append(pickle.load(openfile))
            except EOFError:
                break
    
    return objects[-1]

            