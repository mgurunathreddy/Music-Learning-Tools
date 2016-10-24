# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:41:58 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
import waveio as io
import numpy as np

(fs, x) = io.wavread('../wave/Scale A#Mono.wav')      # Read the samples of input wavefile
x = np.array(x, np.float64)                 # Convert the samples to matlab double data type
x = x/(1.01*np.max(np.abs(x)));             # Normalize sample values
x = x - np.mean(x)                          # Perform mean subtraction to remove DC bias                

trainSampBeg = np.array([1721600, 1976320, 2203648, 2433024, 2636288, 2850816, 3066880, 3309056])
trainSampEnd = np.array([1842688, 2093696, 2323072, 2538624, 2738304, 2955904, 3191936, 3411968])

testSampBeg = np.array([1852032, 2094080, 2322432, 2540544, 2742784, 2965504, 3194368, 3411968])
testSampEnd = np.array([1972224, 2201216, 2432128, 2636416, 2846336, 3064448, 3308160, 3493632])

notesNames = ['sa', 'ri', 'ga', 'ma', 'pa', 'da', 'ni', 'sah'] 
# Save train nate and test notes as wave files
numNotes = np.size(trainSampBeg)
trainDir = '../train_notes/'
testDir = '../test_notes/'


sargamTrain = np.array([])
sargamTest = np.array([])

for i in range(numNotes):
    tempNoteNameTrain = trainDir + notesNames[i] + '.wav'
    tempNoteNameTest = testDir + notesNames[i] + '.wav'
    tempTrain = x[trainSampBeg[i]:trainSampEnd[i]]
    tempTest = x[testSampBeg[i]:testSampEnd[i]]
    #io.wavwrite(tempTrain, fs, tempNoteNameTrain)
    #io.wavwrite(tempTest, fs, tempNoteNameTest)
    sargamTest = np.append(sargamTest, tempTest)
    sargamTrain = np.append(sargamTrain, tempTrain)

io.wavwrite(sargamTest, fs, 'sargamTest.wav')
io.wavwrite(sargamTrain, fs, 'sargamTrain')










