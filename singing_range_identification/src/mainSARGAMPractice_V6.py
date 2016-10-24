# -*- coding: utf-8 -*-
"""
Created on Thu Sep 3 16:23:20 2015
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
#import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import sys, os
import subprocess
import festivalSpeak as speak
import noteCorrection as noteCorrect
import waveio as io

eps = np.finfo(float).eps

#==============================================================================
#filename = '../record/test.wav'
# text = 'Hi, get ready to hear the SARGAM sequnece sung by the teacher'       
# speak.speak(text)
# subprocess.call(['aplay', filename])
#==============================================================================

def recordSARGAM():
    recordFileName = '../record/test.wav'
    text = "Get ready to record your SARGAM for thirty seconds after start command"
    speak.speak(text)
    speak.speak('Start')
    subprocess.call(['arecord',  '-r', '44100', '-d', '30', recordFileName])        # Recording will be done for 30 sec at 44.1 KHz
    text = "This is what you have recorded"
    speak.speak(text)
    subprocess.call(['aplay', recordFileName])

# TODO: Change the fileName to recordFileName
def analysisSARGAM(inputFile):
    #filename = '../../trainee_dataset/sargam4.wav'
    recordFileName = inputFile
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
    
    #==============================================================================
    # # X-axes for plotting functions
    # timeSignal = np.arange(np.size(audio))/sampleRate
    # tempOnsets = np.ones(np.size(onsetTime))
    # timeEnergyCont = np.arange(np.size(medfiltDetectFunc)) * hopSize /sampleRate
    # 
    # plt.figure()
    # plt.subplot(211)
    # plt.plot(timeSignal, audio)
    # plt.stem(onsetTime, tempOnsets, 'r')
    # plt.subplot(212)
    # plt.plot(timeEnergyCont, medfiltDetectFunc/np.max(medfiltDetectFunc), 'g')
    # plt.stem(onsetTime, tempOnsets, 'r')
    #==============================================================================
    
    onsetTimeToFrame = (onsetTime * sampleRate) / hopSize           # Converting onset time back to the frame index
    onsetTimeToFrame = np.array(onsetTimeToFrame, dtype='int')      # Converting float type to int

    plt.figure()
    plt.subplot(311)
    plt.plot(f0)
    plt.stem(onsetTimeToFrame, np.ones(onsetTimeToFrame.size)*500, 'r')
    plt.xlim([0, np.size(f0)])
    
    # Find the spurious onsets based on the stable note frequency and remove them from the list
    totalOnsets = onsetTimeToFrame.size
    trueOnsets = np.array([])
    if (totalOnsets > 8):                                                           # Eight notes hence eight onsets                        
        f0StdThresh = 80                                                            # 50 cents deviation threshold     
        framesToCheck = 100                                                         # Check past frames to decide genuine onset
        for i in range(totalOnsets):
            noteBegIndex = onsetTimeToFrame[i] - framesToCheck
            noteEndIndex = onsetTimeToFrame[i]
            tempF0SegBefore = np.std(np.diff(f0Cent[noteBegIndex:noteEndIndex]))
            tempF0SegAfter = np.std(np.diff(f0Cent[noteEndIndex:noteEndIndex+framesToCheck]))# Check if the pitch is stable after onset. If yes then then, it is a true onset 
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
    
    #==============================================================================
    # plt.figure()
    # f0Time = (np.arange(f0.size) * hopSize)/sampleRate
    # plt.plot(f0Time, f0)
    # plt.stem(onsetTime, tempOnsets+500, 'r')
    #==============================================================================
    plt.subplot(312)
    plt.plot(f0)
    plt.stem(trueOnsets, np.ones(trueOnsets.size)+500, 'r')
    plt.xlim([0, np.size(f0)])
    #==============================================================================
    # plt.figure()
    # plt.plot(f0)
    #==============================================================================
    
    # Find the note values in cent scale and save it in a vector
    numberOfTrueOnsets = trueOnsets.size
    noteValuesCents = np.zeros(numberOfTrueOnsets)       # Note values in cents
    noteValuesHz = np.zeros(numberOfTrueOnsets)     # Note values in Hz
    
    if (numberOfTrueOnsets == 8):                                                   # Checing is the number of notes are exactly 8
        for i in range(numberOfTrueOnsets):
            beginFrames = trueOnsets[i]+200
            endFrames = beginFrames+200
            noteValuesCents[i] = np.median(f0Cent[beginFrames:endFrames])           # Median pitch in cents in the stable region of the note 
            noteValuesHz[i] = np.median(f0[beginFrames:endFrames])
            #plt.figure()
            #plt.plot(f0Cent[beginFrames:endFrames])
            plt.plot(np.arange(beginFrames, endFrames), f0[beginFrames:endFrames], linewidth=3.0)
    
    detectedSargam = noteValuesCents - noteValuesCents[0]                           # Deviation of the detected notes from the tonic note Sa
    trueSargam = np.array([0, 203, 386, 498, 701, 884, 1088, 1200])                 # True SARGAM deviations wrt Sa
    sargamDiff = np.abs(trueSargam - detectedSargam)                                # Deviation bw detected and ground truth
    
    sargmas = [1,2,3,4,5,6,7,8]
    LABELS = ['sa', 'Re', 'Ga' , 'ma', 'Pa', 'da', 'ni', 'Sa']
    
    plt.subplot(313)
    plt.xlabel('SARGAMS')
    plt.ylabel('Deviation in cents')
    plt.title('SARGAM note deviation indicator')
    ax = plt.gca()
    ax.tick_params(axis='x', colors='m')
    ax.tick_params(axis='y', colors='r')
    sargamDiff[0] = 1                                           # Plotting purpose
    barlist = plt.bar(sargmas, sargamDiff, align='center')
    plt.xticks(sargmas, LABELS)
    indxOutTuneNote = np.argwhere(sargamDiff>50)[:, 0]                              # Outof tune notes
    
    for i in range(indxOutTuneNote.size):                                           # Colouring red for outof tune notes
        barlist[indxOutTuneNote[i]].set_color('r')
    plt.show()
    
    endTime = time.time()
    elapsedTime = endTime - beginTime
    print "The total elapsed time is: ", elapsedTime
    np.save('audio.npy', audio)
    np.save('hopSize.npy', hopSize)
    np.save('sampleRate.npy', sampleRate)
    np.save('noteValuesHz.npy', noteValuesHz)
    np.save('indxOutTuneNote.npy', indxOutTuneNote)
    np.save('trueOnsets.npy', trueOnsets)
    #return audio, hopSize, sampleRate, noteValuesHz, indxOutTuneNote, trueOnsets 
        
# Sargam correction 
#noteOnsets = np.array([0, 32632, 186976, 349444, 552030, 729468, 904756, 1092692, 1267548])

def correctSARGAM():
    
    audio = np.load('audio.npy')
    hopSize = np.load('hopSize.npy')
    sampleRate = np.load('sampleRate.npy')
    noteValuesHz = np.load('noteValuesHz.npy')
    indxOutTuneNote = np.load('indxOutTuneNote.npy')
    trueOnsets = np.load('trueOnsets.npy')
    
    signalLength = np.size(audio)
        
    # Ideal SARGAM frequencies
    idealSargamRatios = np.array([1.0000, 1.125, 1.25, 1.333, 1.5, 1.666, 1.875, 2.0000])       # Ideal sargam ratios with sa as the base note        
    idealNoteValuesHz = noteValuesHz[0] * idealSargamRatios                                     # Ideal absolute Note values based on Sa as the base note       
            
    # Frequency ratio of out-of-tune Note
    noteCorrectionRatio = noteValuesHz[indxOutTuneNote]/idealNoteValuesHz[indxOutTuneNote]        
            
    # Frame indicies of the correction required notes
    noteOnsetFramesToSamples = np.array((trueOnsets * hopSize), dtype='int')        
    
    # Find the out-of-tune segments in the signal and then correct it
    correctedSignal = np.copy(audio)        
    #plt.plot(correctedSignal)        
    
    # TODO: 29-06-2016 Signal samples mis-match after note correction wrt orignal. Take the necessary action  
    totalNumOutTuneNotes = np.size(indxOutTuneNote)
    if (totalNumOutTuneNotes >=1):
        if (totalNumOutTuneNotes == 1):                                                     # Only one note is out-of-tune
            if(indxOutTuneNote == 7):                                                       # The note is Eighth or last one is out-of-tune
                noteBeg = noteOnsetFramesToSamples[indxOutTuneNote]                         # There will be only one note     
                noteEnd = signalLength
                tempNote = audio[noteBeg:noteEnd]
                freqScaling = np.array([0, noteCorrectionRatio, 1, noteCorrectionRatio])    # Here noteCorrectionRatio is a real number (scalar) = corresponds to a single note
                print "Entered if note == 1 condition"
                y = noteCorrect.noteCorrection(tempNote, sampleRate, freqScaling)           # TODO: Decide the scaling factor         
                correctedSignal[noteBeg:noteBeg+y.size] = y                                 # Place the corrected note in the right place of the signal
            else:                                                                           # This is other than last note
                noteBeg = noteOnsetFramesToSamples[indxOutTuneNote]                         # Begin sample of the note
                noteEnd = noteOnsetFramesToSamples[indxOutTuneNote+1]                       # End sample is the begin sample of the next note
                tempNote = audio[noteBeg:noteEnd]
                freqScaling = np.array([0, noteCorrectionRatio, 1, noteCorrectionRatio])    # Here noteCorrectionRatio is a real number (scalar) = corresponds to a single note
                print "Entered else note == 1 condition"
                y = noteCorrect.noteCorrection(tempNote, sampleRate, freqScaling)           # TODO: Decide the scaling factor         
                correctedSignal[noteBeg:noteBeg+y.size] = y                                        # Place the corrected note in the right place of the signal
        else:                                                                               # There is more than one note             
            for i in range(totalNumOutTuneNotes):                                                                                   
                if(indxOutTuneNote[i] == 7):                                                # Check if the note is Eighth or last one in the detected out-of-tune notes
                    tempIndx = indxOutTuneNote[i]                                           # Note index of out-of-tune note         
                    noteBeg = noteOnsetFramesToSamples[tempIndx]
                    noteEnd = signalLength
                    tempNote = audio[noteBeg:noteEnd]
                    freqScaling = np.array([0, noteCorrectionRatio[i], 1, noteCorrectionRatio[i]])      # Here noteCorrectionRatio is a real number (scalar) = corresponds to a single note
                    print "Entered multiple note if condition"
                    y = noteCorrect.noteCorrection(tempNote, sampleRate, freqScaling)                   # TODO: Decide the scaling factor           
                    correctedSignal[noteBeg:noteBeg+y.size] = y                                                # Place the corrected note in the right place of the signal
                else:
                    tempIndx = indxOutTuneNote[i]                                                       # Note index of out-of-tune note         
                    noteBeg = noteOnsetFramesToSamples[tempIndx]                                        # Begin sample of the next note will be the end sample of the present note 
                    noteEnd = noteOnsetFramesToSamples[tempIndx+1]                              
                    tempNote = audio[noteBeg:noteEnd]                                                   # Storing note samples in a temporary 
                    freqScaling = np.array([0, noteCorrectionRatio[i], 1, noteCorrectionRatio[i]])    # Here noteCorrectionRatio is a real number (scalar) = corresponds to a single note
                    print "Entered multiple note else condition"
                    y = noteCorrect.noteCorrection(tempNote, sampleRate, freqScaling)           # TODO: Decide the scaling factor           
                    correctedSignal[noteBeg:noteBeg+y.size] = y                                        # Place the corrected note in the right place of the signal
    
        io.wavwrite(correctedSignal, sampleRate, 'synthesisedSARGAM.wav')
        text = 'You did a great job, but still you can improve. The correct sequence of SARGAM is played next'       
        speak.speak(text)
        subprocess.call(['aplay', 'synthesisedSARGAM.wav'])
    
    else:
        text = 'congratulations, you sung like a Nightingle'       
        speak.speak(text)
     







