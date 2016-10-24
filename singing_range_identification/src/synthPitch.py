# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:35:17 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
import numpy as np

def sinewaveSynth(freqs, amp, H, fs):
	"""
	Synthesis of one sinusoid with time-varying frequency
	freqs, amps: array of frequencies and amplitudes of sinusoids
	H: hop size, fs: sampling rate
	returns y: output array sound
	"""

	t = np.arange(H)/float(fs)                              # time array
	lastphase = 0                                           # initialize synthesis phase
	lastfreq = freqs[0]                                     # initialize synthesis frequency
	y = np.array([])                                        # initialize output array
	for l in range(freqs.size):                             # iterate over all frames
		if (lastfreq==0) & (freqs[l]==0):                     # if 0 freq add zeros
			A = np.zeros(H)
			freq = np.zeros(H)
		elif (lastfreq==0) & (freqs[l]>0):                    # if starting freq ramp up the amplitude
			A = np.arange(0,amp, amp/H)
			freq = np.ones(H)*freqs[l]
		elif (lastfreq>0) & (freqs[l]>0):                     # if freqs in boundaries use both
			A = np.ones(H)*amp
			if (lastfreq==freqs[l]):
				freq = np.ones(H)*lastfreq
			else:
				freq = np.arange(lastfreq,freqs[l], (freqs[l]-lastfreq)/H)
		elif (lastfreq>0) & (freqs[l]==0):                    # if ending freq ramp down the amplitude
			A = np.arange(amp,0,-amp/H)
			freq = np.ones(H)*lastfreq
		phase = 2*np.pi*freq*t+lastphase                      # generate phase values
		yh = A * np.cos(phase)                                # compute sine for one frame
		lastfreq = freqs[l]                                   # save frequency for phase propagation
		lastphase = np.remainder(phase[H-1], 2*np.pi)         # save phase to be use for next frame
		y = np.append(y, yh)                                  # append frame to previous one
	return y
