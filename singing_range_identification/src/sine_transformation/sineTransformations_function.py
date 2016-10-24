# function call to the transformation functions of relevance for the sineModel

import numpy as np
#import matplotlib.pyplot as plt
from scipy.signal import get_window
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), '/home/gurunath/coursera/audio_signal_processing/sms-tools-master/software/models/'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath('__file__')), '/home/gurunath/coursera/audio_signal_processing/sms-tools-master/software/transformations/'))
import sineModel as SM
import sineTransformations as ST
import utilFunctions as UF

def analysis(inputFile='tanpura.wav', window='hamming', M=801, N=2048, t=-90, 
	minSineDur=0.01, maxnSines=150, freqDevOffset=20, freqDevSlope=0.02):
	"""
	Analyze a sound with the sine model
	inputFile: input sound file (monophonic with sampling rate of 44100)
	window: analysis window type (rectangular, hanning, hamming, blackman, blackmanharris)	
	M: analysis window size; N: fft size (power of two, bigger or equal than M)
	t: magnitude threshold of spectral peaks; minSineDur: minimum duration of sinusoidal tracks
	maxnSines: maximum number of parallel sinusoids
	freqDevOffset: frequency deviation allowed in the sinusoids from frame to frame at frequency 0   
	freqDevSlope: slope of the frequency deviation, higher frequencies have bigger deviation
	returns inputFile: input file name; fs: sampling rate of input file,
	        tfreq, tmag: sinusoidal frequencies and magnitudes
	"""

#	# size of fft used in synthesis
#	Ns = 512

	# hop size (has to be 1/4 of Ns)
	H = 128

	# read input sound
	(fs, x) = UF.wavread(inputFile)

	# compute analysis window
	w = get_window(window, M)

	# compute the sine model of the whole sound
	tfreq, tmag, tphase = SM.sineModelAnal(x, fs, w, N, H, t, maxnSines, minSineDur, freqDevOffset, freqDevSlope)

	return inputFile, fs, tfreq, tmag


def transformation_synthesis(inputFile, fs, tfreq, tmag, freqScaling = np.array([0, 1.5, 1, 1.5])):
	"""
	Transform the analysis values returned by the analysis function and synthesize the sound
	inputFile: name of input file; fs: sampling rate of input file	
	tfreq, tmag: sinusoidal frequencies and magnitudes
	freqScaling: frequency scaling factors, in time-value pairs
	timeScaling: time scaling factors, in time-value pairs
	"""

	# size of fft used in synthesis
	Ns = 512

	# hop size (has to be 1/4 of Ns)
	H = 128

	# frequency scaling of the sinusoidal tracks 
	ytfreq = ST.sineFreqScaling(tfreq, freqScaling)

	# synthesis 
	y = SM.sineModelSynth(ytfreq, tmag, np.array([]), Ns, H, fs)

	# write output sound 
	outputFile = 'sineModelTransformation.wav'
	UF.wavwrite(y,fs, outputFile)

def mainTanpuraSynth(freqScal):
	
	# analysis
	inputFile, fs, tfreq, tmag = analysis()

	# transformation and synthesis
	transformation_synthesis (inputFile, fs, tfreq, tmag, freqScaling=freqScal)

