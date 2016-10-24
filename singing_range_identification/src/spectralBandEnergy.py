# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:23:20 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""

from essentia import *
from essentia.standard import *
from pylab import *
from numpy import *
import matplotlib.pyplot as plt


filename = '../record/test.wav'

hopSize = 128
frameSize = 2048
sampleRate = 44100
guessUnvoiced = True

run_windowing = Windowing(type='hann', zeroPadding=3*frameSize) # Hann window with x4 zero padding
run_spectrum = Spectrum(size=frameSize * 4)
run_spectEnrg = EnergyBand(startCutoffFrequency=50, stopCutoffFrequency=4000)

pool = Pool();

audio = MonoLoader(filename = filename)()
audio = audio/(1.01*np.max(np.abs(audio)));              # Normalize sample values
audio = audio - np.mean(audio)                                # Perform mean subtraction to remove DC bias                
#plt.figure()
#plt.plot(audio)
audio = EqualLoudness()(audio)

for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
    frame = run_windowing(frame)
    spectrum = run_spectrum(frame)
    spectBandEnrg = run_spectEnrg(spectrum)
    pool.add('allframes_spect_band_enrg', spectBandEnrg)

Enrg = pool['allframes_spect_band_enrg']
meanEnrg = np.mean(Enrg)
framesAboveThresh = np.where(Enrg > meanEnrg)[0]

tempSegmentLength = np.diff(framesAboveThresh)
tempSegmentLength = np.append(tempSegmentLength, tempSegmentLength[-1])
tempSegIndx = np.where(tempSegmentLength>2)[0]

if (np.size(tempSegIndx) == 0):
    startFrameSample = framesAboveThresh[0]
    endFrameFrameSample = framesAboveThresh[-1]
else:
    tempSegIndxDiff = np.diff(tempSegIndx)
    begIndxFrame = np.where(tempSegIndxDiff >= 50)[0]
    
    tempStartFrame = tempSegIndx[begIndxFrame]
    tempEndFrame = tempSegIndx[begIndxFrame+1]
    
    startFrameSample = framesAboveThresh[tempStartFrame]
    endFrameFrameSample = framesAboveThresh[tempEndFrame]


tempMean = np.ones(np.size(Enrg))
tempMean = tempMean * meanEnrg
plt.plot(Enrg)
plt.plot(tempMean)
plt.plot(Enrg[startFrameSample:endFrameFrameSample])

        
        
        
        
        
        
        
        