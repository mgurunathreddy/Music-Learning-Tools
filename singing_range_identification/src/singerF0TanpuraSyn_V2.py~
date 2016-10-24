# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 20:52:56 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
import numpy as np
#import matplotlib.pyplot as plt
import festivalSpeak as speak
import waveio as io
import sys, os
import subprocess
import singerReadWav as sigRedWav
import singerCompMagSpect as sigCompMagSpec
import singerZffF0 as sigZffF0
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), '/home/gurunath/coursera/audio_signal_processing/sms-tools-master/software/models/'))
import singerTWM as sigTWM
import synthPitch as synpitch
import sineTransformations_function as tanpSynth

import time
startTime = time.time()

#text = "Get ready to record the note after saying start"
#speak.speak(text)
#speak.speak('Start')
#subprocess.call(['arecord',  '-r', '44100', '-d', '5', '../record/test.wav'])
#text = "This is what you have recorded"
#speak.speak(text)
#subprocess.call(['aplay', '../record/test.wav'])
def tuneTanpura():
# Newly added
# -----------------------------------------------------------------------------------------------------------------
    text = "Get ready to record the note after saying start"
    speak.speak(text)
    speak.speak('Start')
    subprocess.call(['arecord',  '-r', '44100', '-d', '5', 'test.wav'])
    text = "This is what you have recorded"	
    speak.speak(text)
    subprocess.call(['aplay', 'test.wav'])
# -----------------------------------------------------------------------------------------------------------------
    #trainDir = '../../record/'
    trainDir = './'                                                
    #noteName = 'test'
    fsTrian, xTrain = sigRedWav.readWavfiles(trainDir, 'test')                        # Reads each note
    lenSig = np.size(xTrain)
    
    window = 'hamming'
    M = 1024
    N = 2048
    H = M/4
    mxTrain, pxTrain = sigCompMagSpec.compMagSpect(xTrain, window, N, M, H, fsTrian)    # Computes Mag. and Phase spectrograms
    f0TWM = sigTWM.computTWM(mxTrain, N, fsTrian)                                       # Identifies resonance frequency for ZFF filtering
    #plt.plot(f0TWM)                                             
    nonZeroTWMF0 = f0TWM[f0TWM>0]
    medianTWMF0 = np.median(nonZeroTWMF0)
    
    windSize = np.ceil((1./medianTWMF0) * 1000)                                   # Choose ZFF mean subtraction window emperically as 4ms for v/uv classification
    noteF0Train, zffs, gclocssp1, epssp1 = sigZffF0.getZFFsF0(xTrain, fsTrian, windSize)
    normZFFS = zffs/np.max(np.abs(zffs))                                          # Normalize the ZFFS
    sqrdNormZFFS = np.power(normZFFS, 2)                                          # Normalised energy  
    #plt.plot(sqrdNormZFFS)
    f0Time = gclocssp1/float(fsTrian)
    #==============================================================================
    # plt.plot(f0Time, noteF0Train)
    # plt.plot(zffs)
    #==============================================================================
    
    # Smooth the SoE contour
    def movingaverage(interval, window_size):
        '''
        Computes the moving average by using convolution method i.e., we have filter impulse response to filter the signal
        '''
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    
    runningAvgNormZFFS = movingaverage(sqrdNormZFFS, 400)   # Smoothing SoE contour
    thresh = 1 - np.exp(-10 * runningAvgNormZFFS)           # Determing dynamic threshold
    threshSamples = np.where(thresh > 0.3)[0]               # Take samples which are above threshold
    voicBeg = threshSamples[0]                              # Voiced region begin sample index
    voicEnd = threshSamples[-1]                             # Voiced region end sample index
    
    def find_nearest(array, value):
        idx = (np.abs(array-value)).argmin()
        return idx
    
    f0BegIdx = find_nearest(gclocssp1, voicBeg)             
    f0EndIdx = find_nearest(gclocssp1, voicEnd)
    voicedF0Contour = noteF0Train[f0BegIdx:f0EndIdx]
    medianF0 = np.median(voicedF0Contour)
    
    # Synthesize the obtained F0 contour
    def computF0EveryHop(f0Contour, H):
        pin = 0
        pend = np.size(f0Contour)
        avgF0 = []
        while pin <= pend:
            tempF0Cont = f0Contour[pin:pin+H]
            tempF0 = tempF0Cont[tempF0Cont>0]
            if np.size(tempF0) != 0:
                meanF0 = np.mean(tempF0)
                avgF0 = np.append(avgF0, meanF0)
            else:
                avgF0 = np.append(avgF0, 0)
            pin = pin + H
        return avgF0
                
    f0Contour = np.zeros(lenSig)
    f0Contour[gclocssp1[f0BegIdx:f0EndIdx]] = voicedF0Contour 
    f0Interval = (20 * fsTrian)/1000                                                    # Compute f0 for every 20ms
    meanF0Contour = computF0EveryHop(f0Contour, f0Interval)
    #plt.plot(meanF0Contour)
    
    # Synthesize the singers melody contour
    yf0 = synpitch.sinewaveSynth(meanF0Contour, .6, H, fsTrian)
    #==============================================================================
    # plt.figure()
    # plt.plot(yf0)
    #==============================================================================
    io.wavwrite(yf0, fsTrian, 'traineeMelody.wav')
    text = 'Hi, get ready to hear your sung melody'       
    speak.speak(text)
    subprocess.call(['aplay', 'traineeMelody.wav'])
    
    #medianF0 = 140.0        # Remove this hard coded value of F0
    # Change the pitch of the tanpura according to the singers F0 value
    tanpuraTuningFreq = 139.0                         # Our Tanpura is tuned to 139Hz (get it from spectrogram)
    scalingFactor = medianF0/tanpuraTuningFreq      # Tanpura scaling factor
    freqScaling = np.array([0, scalingFactor, 1, scalingFactor])
    tanpSynth.mainTanpuraSynth(freqScaling)
    
    text = 'Playing original Tanpura'       
    speak.speak(text)
    
    #for _ in range(4):
    subprocess.call(['aplay', 'tanpura.wav'])
    
    text = 'Your fundamental frequency is approximately' + ' ' + str(np.int(medianF0)) + ' ' + 'Hertz'      
    speak.speak(text)
    
    text = 'Playing frequency tuned Tanpura according to your fundamental frequency'       
    speak.speak(text)
    for _ in range(2):
        subprocess.call(['aplay', 'sineModelTransformation.wav'])
    
    endTime = time.time()
    elapsed = endTime - startTime 
    
