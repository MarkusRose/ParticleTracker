#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2015-11-30
# email: markus.m.rose@gmail.com
#=====================================


import numpy as np
import pandas as pd
import math
from scipy.optimize import curve_fit
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os


#========================================
# Program functions
#========================================

def readTracks(infile):
    tracks = []
    return tracks

def testingArea():
    print("Hello World!")

    print("Read Tracks!")
    

    return



#++++++++++++++++++++++++++++++++++++++++

#====================================
#The big MAIN
#====================================
def doAnalysis(trackfile,pixelsize=0.100,frametime=0.1,bCleanUpTracks=True,bSingleTrackEndToEnd=False,bSingleTrackMSDanalysis=True,bCombineTrack=True):
    #combined Track input
    #plotting parameters
    Dfactor = pixelsize*pixelsize/frametime

    lenMSD_ct = 300
    plotlen = 30 #gives the range of the distribution plots
    numberofbins = 200
    small = 20
    large = 100

    #single track analysis input
    minTrLength = 15
    
    if (not bSingleTrackEndToEnd) and (not bSingleTrackMSDanalysis) and (not bCombineTrack):
        return

    tracks = readTracks(trackfile)

    path = os.path.dirname(trackfile)
    spng = os.path.join(path,"SingleStateAnalysis")
    if not os.path.isdir(spng):
        os.mkdir(spng)
    
    if bCleanUpTracks:
        print()
        print("Cleaning Track File from NAN")
        print("----------------------------")
        cleanTracksFile(tracks,path+"/cleanedTracks.txt")
    
    considered = []
    for i in tracks:
        if len(i) >= minTrLength:
            considered.append(i)
    if len(considered) == 0:
        print("Tracks are too short! Please adjust 'minTrackLen' to a lower value!")
        #raw_input("Please restart again...")
        return
    if bSingleTrackEndToEnd:
        print()
        print()
        print("Starting End-To-End Displacement Analysis for single tracks")
        print("-----------------------------------------------------------")
        eehisto = eedispllist(considered,numberofbins=numberofbins,path=spng)
    if len(considered) > 100:
        considered = considered[:]
    
    if bSingleTrackMSDanalysis:
        print()
        print()
        print("Starting Diffusion Constant Analysis for single tracks")
        print("------------------------------------------------------")
        diffChisto = diffConstDistrib(considered,pixelsize,frametime,Dfactor,numberofbins=numberofbins,path=spng)
    if bCombineTrack:
        print()
        print()
        print("Starting Combined Track Analysis")
        print("--------------------------------")
        analyzeCombinedTrack(considered,pixelsize,frametime,Dfactor,lenMSD=lenMSD_ct,numberofbins=numberofbins,plotlen=plotlen,path=spng)
    return
#=====================================



if __name__ == "__main__":
    testingArea()

