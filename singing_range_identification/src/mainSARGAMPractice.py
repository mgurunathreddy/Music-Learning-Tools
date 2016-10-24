# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 16:23:20 2015
Description: The SARGAM sequence is divided into notes by spectral flux based method. The fundamental frequneyc of each is obtained
             The successive note ratios are determined. A score is given for each note based on the note ratio deviation according to the musical scale.   
Inputs: Wave file recorded from the microphone containing the sequence of notes.
Outputs: Scores for each note
@author: Gurunath Reddy M

"""

from essentia import *
from essentia.standard import *
from pylab import *
from numpy import *
import matplotlib.pyplot as plt

#filename = '../record/test.wav'

filename = '../trainee_dataset/sargam.wav'

hopSize = 128
frameSize = 2048
sampleRate = 44100.0

run_windowing = Windowing(type='hann', zeroPadding=2*frameSize) # Hann window with x4 zero padding
run_spectrum = Spectrum(size=frameSize * 4)
run_spectEnrg = EnergyBand(startCutoffFrequency=50, stopCutoffFrequency=4000)

pool = Pool();

audio = MonoLoader(filename = filename)()
audio = audio/(1.01*np.max(np.abs(audio)));              # Normalize sample values
audio = audio - np.mean(audio)                                # Perform mean subtraction to remove DC bias                

#lpf = LowPass(cutoffFrequency=2000)
#audio = lpf(audio)

N = frameSize + 2*frameSize
binFreq = sampleRate/N

#plt.figure()
#plt.plot(audio)
#audio = EqualLoudness()(audio)
#spectralFlux = Flux(halfRectify=True)
detectionFunction = np.array([])
onsetDetection = OnsetDetection(method='flux')

timeEnergy = Energy()
energy = essentia.array([])
spectralBandEnrg = np.array([])

# Pitch detection by YIN
minf0 = 50
maxf0 = 500
pitchYin= PitchYinFFT(minFrequency = minf0, maxFrequency = maxf0)
f0 = np.array([])
for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
    frame = run_windowing(frame)
    spectrum = run_spectrum(frame)
    #spectrum = np.log10(spectrum)
    spectBandEnrg = run_spectEnrg(spectrum[5:100])
    spectralBandEnrg = np.append(spectralBandEnrg, spectBandEnrg)
    #pool.add('allframes_spect_band_enrg', spectBandEnrg)
    #specGram = pool.add('allframe_spectrum', spectrum);
    #flux = np.append(flux, spectralFlux(spectrum))
    detectionFunction = np.append(detectionFunction, onsetDetection(spectrum[50:200], spectrum[5:200]))
    energy = np.append(energy, timeEnergy(frame))
    
    f0t = pitchYin(spectrum)
    f0 = np.append(f0, f0t[0])
    
plt.plot(f0)    
eps = np.finfo(float).eps
f0[f0 < eps] = eps
f0Cent = 1200 * np.log2(f0/55.0)
plt.plot(f0Cent)

#specGram = pool['allframe_spectrum']
detectionFunction = np.power(detectionFunction, 2)
detectionFunction = detectionFunction/np.max(detectionFunction)
plt.plot(detectionFunction)
#plt.plot(np.log10(detectionFunction))
from scipy.signal import medfilt
medfiltDetectFunc = medfilt(detectionFunction, 11)
plt.plot(medfiltDetectFunc)

plt.figure()
plt.plot(energy)

sumOfDetectionFunctons = medfiltDetectFunc/np.max(medfiltDetectFunc) + energy/np.max(energy)
plt.figure()
plt.plot(sumOfDetectionFunctons)

#detectionFunction = spectralBandEnrg
medfiltDetectFunc = sumOfDetectionFunctons
flux = essentia.array(medfiltDetectFunc)
flux = np.reshape(flux, (1, flux.size))

frameRate = sampleRate/hopSize

onsetDection = Onsets(alpha=0.1, delay=200, frameRate=frameRate, silenceThreshold=0.01)
weights = essentia.array([1])
weights = np.reshape(weights, (1,))
onsetTime = onsetDection(flux, weights)    

timeSignal = np.arange(np.size(audio))/sampleRate
tempOnsets = np.ones(np.size(onsetTime))
timeEnergyCont = np.arange(np.size(energy)) * hopSize /sampleRate

plt.figure()
plt.plot(timeSignal, audio)
plt.stem(onsetTime, tempOnsets, 'r')
#plt.plot(timeEnergyCont, energy, 'g')

onsetTimeToFrame = (onsetTime * sampleRate) / hopSize
onsetTimeToFrame = np.array(onsetTimeToFrame, dtype='int')

plt.figure()
plt.plot(f0)
plt.stem(onsetTimeToFrame, np.ones(onsetTimeToFrame.size)*500, 'r')

# Find the spurious onsets and remove them from the list

totalOnsets = onsetTimeToFrame.size
if (totalOnsets > 8):
    f0StdThresh = 50
    framesToCheck = 100
    for i in range(totalOnsets):
        noteBegIndex = onsetTimeToFrame[i] - framesToCheck
        noteEndIndex = onsetTimeToFrame[i]
        tempF0Seg = np.std(f0Cent[noteBegIndex:noteEndIndex])
        if tempF0Seg < f0StdThresh:
            print "The spurious onset is: ", i  
            onsetTimeToFrame[i] = 0

nonZeroOnsetIndicies = np.argwhere(onsetTimeToFrame > 0)[:, 0]
trueOnsets = onsetTimeToFrame[nonZeroOnsetIndicies]

plt.plot(f0)
plt.stem(trueOnsets, np.ones(trueOnsets.size)+500, 'r')

# Find the note values in cent scale and save it in a vector
numberOfTrueOnsets = trueOnsets.size
noteValues = np.zeros(numberOfTrueOnsets)
if (numberOfTrueOnsets == 8):
    for i in range(numberOfTrueOnsets):
        beginFrames = trueOnsets[i]+200
        endFrames = beginFrames+200
        noteValues[i] = np.median(f0Cent[beginFrames:endFrames])
        #plt.figure()
        #plt.plot(f0Cent[beginFrames:endFrames])
        plt.plot(np.arange(beginFrames, endFrames), f0[beginFrames:endFrames])

detectedSargam = noteValues - noteValues[0]
trueSargam = np.array([0, 203, 386, 498, 701, 884, 1088, 1200])
sargamDiff = np.abs(trueSargam - detectedSargam)

sargmas = [1,2,3,4,5,6,7,8]
LABELS = ['sa', 'Re', 'Ga' , 'ma', 'Pa', 'da', 'ni', 'sa']

plt.figure()

#Set tick colors:
ax = plt.gca()
ax.tick_params(axis='x', colors='blue')
ax.tick_params(axis='y', colors='red')
sargamDiff[0] = 1
barlist = plt.bar(sargmas, sargamDiff, align='center')
plt.xticks(sargmas, LABELS)

indxOutTuneNote = np.argwhere(sargamDiff>50)[:, 0]

for i in range(indxOutTuneNote.size):
    barlist[indxOutTuneNote[i]].set_color('r')


        
        
        
        
        
        
        
        