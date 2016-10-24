# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 22:29:21 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""

import zff as zff
import numpy as np
import smooth as smooth

def getZFFsF0(xTest, fsTrian, windSize):
    
    [zffs, gclocssp1, epssp1, f0sp1] = zff.zff(xTest, fsTrian, windSize) # Compute the zff of x
    zf1 = np.copy(zffs)
    zffs[zffs>0] = 1 # To find zero crossings, place value 1 at all locations zffs>0
    zffs[zffs<0] = -1 # Place value -1 at all locations zffs<0
    gci = np.where(np.diff(zffs) == 2)[0] # Take difference and look for the positions of value 2
    #es = np.abs(zf1[gci+1]-zf1[gci-1]) # Positions of value 2 are the instants of zero crossings
    T0 = np.diff(gci) # Finding period interms of sample number 
    T0 = T0/float(fsTrian) # Period in seconds
    f0 = 1.0/T0 # Frequency in Hz
    f0 = np.append(f0, f0[-1], f0[-1]) # Filling holes created by two difference operation
    # Smoothing the melody to remove high frequency contents
    f0Smooth = smooth.smooth(f0, 20, 'flat')
    f0Smooth = smooth.smooth(f0Smooth, 10, 'flat')
    return f0Smooth, zf1, gclocssp1, epssp1