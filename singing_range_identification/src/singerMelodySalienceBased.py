# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 11:58:22 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""

#import sys, csv, os
from essentia import *
from essentia.standard import *
from pylab import *
from numpy import *
import matplotlib.pyplot as plt
#sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../../software/models/'))
#import utilFunctions as UF

def getTraineeMelody(filename):
    hopSize = 128
    frameSize = 2048
    sampleRate = 44100
    guessUnvoiced = True
    
    run_windowing = Windowing(type='hann', zeroPadding=3*frameSize) # Hann window with x4 zero padding
    run_spectrum = Spectrum(size=frameSize * 4)
    run_spectral_peaks = SpectralPeaks(minFrequency=50,
                                       maxFrequency=10000,
                                       maxPeaks=100,
                                       sampleRate=sampleRate,
                                       magnitudeThreshold=0,
                                       orderBy="magnitude")
    run_pitch_salience_function = PitchSalienceFunction(magnitudeThreshold=30)
    run_pitch_salience_function_peaks = PitchSalienceFunctionPeaks(minFrequency=100, maxFrequency=300)
    run_pitch_contours = PitchContours(hopSize=hopSize, peakFrameThreshold=0.8)
    run_pitch_contours_melody = PitchContoursMelody(guessUnvoiced=guessUnvoiced,
                                                    hopSize=hopSize)
    run_spectEnrg = EnergyBand(startCutoffFrequency=50, stopCutoffFrequency=4000)

    pool = Pool();
    
    audio = MonoLoader(filename = filename)()
    audio = audio/(1.01*np.max(np.abs(audio)));              # Normalize sample values
    audio = audio - np.mean(audio)                                # Perform mean subtraction to remove DC bias                
    plt.figure()
    plt.plot(audio)
    audio = EqualLoudness()(audio)
    
    for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
        frame = run_windowing(frame)
        spectrum = run_spectrum(frame)
        spectBandEnrg = run_spectEnrg(spectrum)
        pool.add('allframes_spect_band_enrg', spectBandEnrg)

        peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)
            
        salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
        salience_peaks_bins, salience_peaks_saliences = run_pitch_salience_function_peaks(salience)
        
        pool.add('allframes_salience_peaks_bins', salience_peaks_bins)
        pool.add('allframes_salience_peaks_saliences', salience_peaks_saliences)
    
    contours_bins, contours_saliences, contours_start_times, duration = run_pitch_contours(
            pool['allframes_salience_peaks_bins'],
            pool['allframes_salience_peaks_saliences'])
    pitch, confidence = run_pitch_contours_melody(contours_bins,
                                                  contours_saliences,
                                                  contours_start_times,
                                                  duration)
    
#    yf0 = UF.sinewaveSynth(pitch, .6, hopSize, sampleRate)
    
    time = hopSize*arange(size(pitch))/float(sampleRate)
    pitch[pitch==0]=nan

    plt.figure()
    plt.subplot(211)
    plot(time, pitch, color='k', linewidth = 2)
    plt.title('Trainees Melody Contour')
    
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
        begIndxFrame = np.where(tempSegIndxDiff >= 100)[0]
        
        tempStartFrame = tempSegIndx[begIndxFrame]
        tempEndFrame = tempSegIndx[begIndxFrame+1]
        
        startFrameSample = framesAboveThresh[tempStartFrame]
        endFrameFrameSample = framesAboveThresh[tempEndFrame]

#    tempSegIndxDiff = np.diff(tempSegIndx)
#    begIndxFrame = np.where(tempSegIndxDiff >= 100)[0]
#    
#    tempStartFrame = tempSegIndx[begIndxFrame]
#    tempEndFrame = tempSegIndx[begIndxFrame+1]
#    
#    startFrameSample = framesAboveThresh[tempStartFrame]
#    endFrameFrameSample = framesAboveThresh[tempEndFrame]
    
    tempMean = np.ones(np.size(Enrg))
    tempMean = tempMean * meanEnrg
    
    plt.subplot(212)
    plt.plot(Enrg)
    plt.plot(tempMean)

    voicedPitch = pitch[startFrameSample:endFrameFrameSample]    
    
#    UF.wavwrite(yf0, sampleRate, 'traineeMelody.wav')
    return voicedPitch
