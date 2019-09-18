#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2019-09-17
# email: rosemm2@mcmaster.ca
#=====================================

import numpy as np
import math
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
import os

from AnalysisTools.ana_singlestate_legacy import doAnalysis

if __name__=="__main__":

    #========================================
    # User Input Variables
    #========================================
    filelist = sys.argv[1:]

    frametime = 1 # frame interval in s
    pixelsize = 0.067 # in um

    bSingleTrackMSDanalysis = True
    bCombineTrack = True

    #single track analysis input
    minTrLength = 20
    fitrange = 0.5

    for trackfile in filelist:
        print()
        print("***********************************************************")
        print("Starting One State Analysis on: {:}".format(trackfile))
        doAnalysis(trackfile,pixelsize=pixelsize,frametime=frametime,minTrLength=minTrLength,fitrange=fitrange,bSingleTrackMSDanalysis=bSingleTrackMSDanalysis,bCombineTrack=bCombineTrack)

