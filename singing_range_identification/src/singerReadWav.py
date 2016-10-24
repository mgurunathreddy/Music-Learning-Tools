# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:19:04 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
import waveio as io
import numpy as np

def readWavfiles(trainDir, notesName):

    trainFilePath = trainDir + notesName + '.wav'
    (fs, xtrain) = io.wavread(trainFilePath)    # Read train sample note
    xtrain = np.array(xtrain, np.float64)                       # Convert the samples to matlab double data type
    xtrain = xtrain/(1.01*np.max(np.abs(xtrain)));              # Normalize sample values
    xtrain = xtrain - np.mean(xtrain)                                # Perform mean subtraction to remove DC bias                
    return fs, xtrain