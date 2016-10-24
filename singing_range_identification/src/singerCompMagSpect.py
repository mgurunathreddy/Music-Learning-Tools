# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:28:59 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
from scipy.signal import get_window
import dftStft as stft

def compMagSpect(xtrain, window, N, M, H, fs): 
    w = get_window(window, M)
    mxTrain, pxTrain = stft.stftAnal(xtrain, fs, w, N, H) # mx and px are the magnitude and phase spectrum
    return mxTrain, pxTrain