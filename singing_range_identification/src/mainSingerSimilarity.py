# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 16:11:13 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
import numpy as np
from scipy.signal import _savitzky_golay as savgol_filter
import matplotlib.pyplot as plt
import zff as zff
import festivalSpeak as speak
import waveio as io
import sys, os
import subprocess
import singerReadWav as sigRedWav
import singerCompMagSpect as sigCompMagSpec
import singerTWM as sigTWM
import smooth as smooth
import singerZffF0 as sigZffF0
import singerMelodySalienceBased as singMelSali
#sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../../software/models/'))
#import utilFunctions as UF
import synthPitch as synpitch
import time

notesNames = ['sa', 'ri', 'ga', 'ma', 'pa', 'da', 'ni', 'sah']  # Notes to be identified
notesAvgFreq = np.array([236, 264, 290, 300, 345, 391, 440, 463])
trainDir = '../train_notes/'                                    # Directory where train notes are present
testDir = '../test_notes/'                                      # Directory where test notes are present

text = 'Enter the note name you want to practice: '
getNoteName = raw_input('Enter the note name you want to practice: ')
text = "You will be going to hear the note in next 4 Seconds"
speak.speak(text)

trainNoteFileName = trainDir + getNoteName + '.wav'
time.sleep(4)
subprocess.call(['aplay', trainNoteFileName])

text = "Get ready for your turn to record the note after start prompt"
speak.speak(text)
speak.speak('Start')
subprocess.call(['arecord',  '-r', '44100', '-d', '5', '../record/test.wav'])
text = "This is what you have recorded"
speak.speak(text)
subprocess.call(['aplay', '../record/test.wav'])

indexOfNote = notesNames.index(getNoteName)
fileName = '../record/test.wav'
pitch = singMelSali.getTraineeMelody(fileName)
whereAreNans = np.isnan(pitch)
pitch[whereAreNans] = 0
meanPitch = np.mean(pitch[pitch>0])

#fs, wav = io.wavread(fileName)

if(meanPitch >= notesAvgFreq[indexOfNote]-10 and meanPitch <= notesAvgFreq[indexOfNote]+10):
    text = "Your pitch range is comparable with the singers pitch range"
    speak.speak(text)
else:
    text = "Sorry, your pitch range is not comparable. You can try one more time"
    speak.speak(text)
    
text = 'Your sung Melody will be played in next 4 Seconds'       
speak.speak(text)
hopSize = 128
sampleRate = 44100
yf0 = synpitch.sinewaveSynth(pitch, .6, hopSize, sampleRate)
io.wavwrite(yf0, sampleRate, 'traineeMelody.wav')
plt.plot(pitch)
subprocess.call(['aplay', 'traineeMelody.wav'])


#fsTrian, xTrain = sigRedWav.readWavfiles(trainDir, noteName)                        # Reads each note
#mxTrain, pxTrain = sigCompMagSpec.compMagSpect(xTrain, window, N, M, H, fsTrian)    # Computes Mag. and Phase spectrograms
#f0TWM = sigTWM.computTWM(mxTrain, N, fsTrian)                                       # Identifies resonance frequency for ZFF filtering
#plt.plot(f0TWM)                                             
#

#[fs, x] = io.wavread('../trainee_dataset/2Octaves.wav')
#x = np.array(x, np.float64) # Datatype conversion is must for python to compatable with matlab
#x = x/(1.01*np.max(np.abs(x)));
#windSize = 2.5                                    # Choose ZFF mean subtraction window emperically as 4ms for v/uv classification
#noteF0Train = sigZffF0.getZFFsF0(x, fs, windSize)
#plt.plot(noteF0Train)



#
#diffNoteF0Train = np.diff(noteF0Train)
#absDiff = np.abs(diffNoteF0Train)
#meanDiff = np.mean(absDiff)
#requIndi = np.where(absDiff <= meanDiff)[0]
#tempF0 = noteF0Train[requIndi]
#diffTempF0 = np.abs(np.diff(tempF0))
#meanTempF0 = np.mean(diffTempF0)
#indxActualTrainMelody = np.where(diffTempF0 < meanTempF0)[0]
#actualF0TrainMelody = noteF0Train[indxActualTrainMelody]
#plt.figure()
#plt.plot(noteF0Train)
##plt.plot(actualF0TrainMelody)
#
#
#io.savemat('../train_melodies/'+ noteName+'.mat', mdict={noteName:noteF0Train})
#noteFreq = io.loadmat('../train_melodies/'+noteName+'.mat', struct_as_record=True)
#freq = np.reshape(noteFreq[noteName], -1)
#plt.plot(freq)
#
#noteName = notesNames[7]
#windSize = 5 # Choose ZFF mean subtraction window emperically as 4ms for v/uv classification
#fsTrian, xTrain = sigRedWav.readWavfiles(trainDir, noteName)
#noteF0Train = sigZffF0.getZFFsF0(xTrain, fsTrian, windSize)
#plt.plot(noteF0Train)
#
#fsTest, xTest = sigRedWav.readWavfiles(testDir, noteName)
#noteF0Test = sigZffF0.getZFFsF0(xTest, fsTest, windSize)
#plt.plot(noteF0Test)
