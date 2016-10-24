# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:35:37 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""

import f0Detect as f0Detect
from scipy.signal import  medfilt

def computTWM(mxTrain, N, fs):

    t = -60.0           # Magnitude threshold for TWM
    minf0 = 100
    maxf0 = 1000
    f0etr = 5           # Error threshold in HZ    
    # Performing TWM to get the f0 contour
    f0 = f0Detect.f0Detection(mxTrain, fs, N, t, minf0, maxf0, f0etr)        # Getting f0 by TWM
    # Clean obtained f0
    f0MedFilt = medfilt(f0, 3)
    f0MedFilt = medfilt(f0MedFilt, 5)
    return f0MedFilt
