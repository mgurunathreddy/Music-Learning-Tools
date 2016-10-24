# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:23:20 2015
Description: The SARGAM sequence is divided into notes by spectral flux based method. The fundamental frequneyc of each is obtained
             The successive note ratios are determined. A score is given for each note based on the note ratio deviation according to the musical scale.   
Inputs: Wave file recorded from the microphone containing the sequence of notes.
Outputs: Scores for each note
@author: Gurunath Reddy M

"""

import time as time
beginTime = time.time()
from essentia import *
from essentia.standard import *
from pylab import *
from numpy import *
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import sys, os
import subprocess
import festivalSpeak as speak

eps = np.finfo(float).eps

#==============================================================================
#filename = '../record/test.wav'
filename = '../trainee_dataset/sargam1.wav'
# text = 'Hi, get ready to hear the SARGAM sequnece sung by the teacher'       
# speak.speak(text)
# subprocess.call(['aplay', filename])
#==============================================================================

#==============================================================================
# recordFileName = '../record/test.wav'
# text = "Get ready to record your SARGAM after start command"
# speak.speak(text)
# speak.speak('Start')
# subprocess.call(['arecord',  '-r', '44100', '-d', '30', recordFileName])        # Recording will be done for 30 sec at 44.1 KHz
# text = "This is what you have recorded"
# speak.speak(text)
# subprocess.call(['aplay', recordFileName])
#==============================================================================

# TODO: Change the fileName to recordFileName
recordFileName = filename
audio = MonoLoader(filename = recordFileName)()
audio = audio/(1.01*np.max(np.abs(audio)));     # Normalize sample values
audio = audio - np.mean(audio)                  # Perform mean subtraction to remove DC bias                

hopSize = 128
frameSize = 2048
sampleRate = 44100.0

N = frameSize + 2*frameSize         # Essentia FFT points                                 
binFreq = sampleRate/N              # Essentia bin resolution
frameRate = sampleRate/hopSize      # frameRate required by Onsets function
weights = essentia.array([1])       # Weights required by Onsets function to give different weights for different novality functions    
weights = np.reshape(weights, (1,)) # Should be a vector required by Onsests function

run_windowing = Windowing(type='hann', zeroPadding=2*frameSize)     # Hann window with x4 zero padding
run_spectrum = Spectrum(size=frameSize * 4)                         # Spectrum with FFT points = 4 * frameSize
onsetDetection = OnsetDetection(method='flux')                      # Initilizing object for spectral flux based onset detection method
timeEnergy = Energy()                                               # Signal energy for onset detection
onsetDection = Onsets(alpha=0.1, delay=200, frameRate=frameRate, silenceThreshold=0.01)

# Pitch detection by YIN
minf0 = 50
maxf0 = 500
pitchYin= PitchYinFFT(minFrequency = minf0, maxFrequency = maxf0)   # YIN based pitch detection method

detectionFunction = essentia.array([])                              # Vector to store flux 
energy = essentia.array([])                                         # Vector to store energy
f0 = np.array([])                                                   # Vector to store f0
for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
    frame = run_windowing(frame)
    spectrum = run_spectrum(frame)
    detectionFunction = np.append(detectionFunction, onsetDetection(spectrum[50:200], spectrum[50:200]))
    energy = np.append(energy, timeEnergy(frame))
    f0t = pitchYin(spectrum)                                        # YIN outputs pitch and its confidence 
    f0 = np.append(f0, f0t[0])
    
#plt.plot(f0)    
f0[f0 < eps] = eps                  # Make non-zero F0
f0Cent = 1200 * np.log2(f0/55.0)    # Convert frequency to cent scale
#plt.plot(f0Cent)

# Non linear filtering of the detection function to emphasize the onsests
detectionFunction = np.power(detectionFunction, 2)                                              # Squaring    
detectionFunction = detectionFunction/np.max(detectionFunction)                                 # Normalizing
medfiltDetectFunc = medfilt(detectionFunction, 11)                                              # Median filtering to remove outliers    
#plt.plot(medfiltDetectFunc)
sumOfDetectionFunctons = medfiltDetectFunc/np.max(medfiltDetectFunc) + energy/np.max(energy)    # Summing both the functions to emphasize the weak onsets
#plt.figure()
#plt.plot(sumOfDetectionFunctons)

#detectionFunction = spectralBandEnrg
#medfiltDetectFunc = sumOfDetectionFunctons
sumOfDetectionFunctons = essentia.array(sumOfDetectionFunctons)
sumOfDetectionFunctons = np.reshape(sumOfDetectionFunctons, (1, sumOfDetectionFunctons.size))   # Make it as a vector suitable for onsets function 

onsetTime = onsetDection(sumOfDetectionFunctons, weights)                 # Onset instants are detected from the combined onset detection function    

# X-axes for plotting functions
timeSignal = np.arange(np.size(audio))/sampleRate
tempOnsets = np.ones(np.size(onsetTime))
timeEnergyCont = np.arange(np.size(energy)) * hopSize /sampleRate

plt.figure()
plt.plot(timeSignal, audio)
plt.stem(onsetTime, tempOnsets, 'r')
plt.plot(timeEnergyCont, energy, 'g')

onsetTimeToFrame = (onsetTime * sampleRate) / hopSize           # Converting onset time back to the frame index
onsetTimeToFrame = np.array(onsetTimeToFrame, dtype='int')      # Converting float type to int
#plt.figure()
#plt.plot(f0)
#plt.stem(onsetTimeToFrame, np.ones(onsetTimeToFrame.size)*500, 'r')

# Find the spurious onsets based on the stable note frequency and remove them from the list
totalOnsets = onsetTimeToFrame.size
trueOnsets = np.array([])
if (totalOnsets > 8):                                                           # Eight notes hence eight onsets                        
    f0StdThresh = 80                                                            # 50 cents deviation threshold     
    framesToCheck = 100                                                         # Check past frames to decide genuine onset
    for i in range(totalOnsets):
        noteBegIndex = onsetTimeToFrame[i] - framesToCheck
        noteEndIndex = onsetTimeToFrame[i]
        tempF0SegBefore = np.std(f0Cent[noteBegIndex:noteEndIndex])
        tempF0SegAfter = np.std(f0Cent[noteEndIndex:noteEndIndex+framesToCheck])# Check if the pitch is stable after onset. If yes then then, it is a true onset 
        #print "The variance of ", i, 'is: ', tempF0SegBefore, tempF0SegAfter        
        #plt.plot(np.arange(noteEndIndex, noteEndIndex+framesToCheck), f0Cent[noteEndIndex:noteEndIndex+framesToCheck])        
        if ((tempF0SegBefore > f0StdThresh) and (tempF0SegAfter < f0StdThresh)):                                             # If past frames pitch is constant, then the onset is a spurious one 
            #print "Genuine onset is: ", i  
            trueOnsets = np.append(trueOnsets, onsetTimeToFrame[i])
            #print tempF0SegAfter

#==============================================================================
# nonZeroOnsetIndicies = np.argwhere(onsetTimeToFrame == 0)[:, 0]                  # Locatins of genuine onsets
# trueOnsets = onsetTimeToFrame[nonZeroOnsetIndicies]                             # Genuine onsets
#==============================================================================

plt.figure()
plt.plot(f0)
plt.stem(trueOnsets, np.ones(trueOnsets.size)+500, 'r')

# Find the note values in cent scale and save it in a vector
numberOfTrueOnsets = trueOnsets.size
noteValues = np.zeros(numberOfTrueOnsets)
if (numberOfTrueOnsets == 8):                                                   # Checing is the number of notes are exactly 8
    for i in range(numberOfTrueOnsets):
        beginFrames = trueOnsets[i]+200
        endFrames = beginFrames+200
        noteValues[i] = np.median(f0Cent[beginFrames:endFrames])                # Median pitch in cents in the stable region of the note 
        #plt.figure()
        #plt.plot(f0Cent[beginFrames:endFrames])
        plt.plot(np.arange(beginFrames, endFrames), f0[beginFrames:endFrames])

detectedSargam = noteValues - noteValues[0]                                     # Deviation of the detected notes from the tonic note Sa
trueSargam = np.array([0, 203, 386, 498, 701, 884, 1088, 1200])                 # True SARGAM deviations wrt Sa
sargamDiff = np.abs(trueSargam - detectedSargam)                                # Deviation bw detected and ground truth

sargmas = [1,2,3,4,5,6,7,8]
LABELS = ['sa', 'Re', 'Ga' , 'ma', 'Pa', 'da', 'ni', 'Sa']

plt.figure()
plt.xlabel('SARGAMS')
plt.ylabel('Deviation in cents')
plt.title('SARGAM note deviation indicator')
ax = plt.gca()
ax.tick_params(axis='x', colors='m')
ax.tick_params(axis='y', colors='red')
sargamDiff[0] = 1                                           # Plotting purpose
barlist = plt.bar(sargmas, sargamDiff, align='center')
plt.xticks(sargmas, LABELS)

indxOutTuneNote = np.argwhere(sargamDiff>50)[:, 0]                              # Outof tune notes

for i in range(indxOutTuneNote.size):                                           # Colouring red for outof tune notes
    barlist[indxOutTuneNote[i]].set_color('r')

endTime = time.time()
elapsedTime = endTime - beginTime
print "The total elapsed time is: ", elapsedTime
        
    
    
    
    
    
    