# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:09:56 2015
Description:
Inputs:
Outputs:
@author: Gurunath Reddy M

"""
from subprocess import PIPE, Popen

def speak(text):
    process = Popen(['festival', '--tts'], stdin=PIPE)
    process.stdin.write(text + '\n')
    process.stdin.close()
    process.wait()
