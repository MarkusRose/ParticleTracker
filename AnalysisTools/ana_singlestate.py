#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2015-11-30
# email: markus.m.rose@gmail.com
#=====================================


import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import math
import matplotlib.pyplot as plt
import sys
import os

#import matplotlib
#matplotlib.use('Agg')

#========================================
# Program functions
#========================================

def readTracks(infile):
    df = pd.read_csv(infile,sep=',',header=0)
    return df 

def combineTracks(dafa):

    alltracks = dafa['particle_id'].unique()

    columns = ['x','y']
    dfcomb = pd.DataFrame(columns=columns)

    ffirst = True
    for elem in alltracks:
        dfsave =  dafa[dafa['particle_id']==elem][columns] - dafa[dafa['particle_id']==elem][columns].iloc[0]
        if ffirst:
            dfcomb = dfcomb.append(dfsave)
            ffirst = False
        else:
            dfsave = dfsave[columns] + dfcomb[columns].iloc[-1]
            dfcomb = dfcomb.append(dfsave[1:])

    dfcomb.to_csv("combinedTrack.csv",index=False)
    return dfcomb 


def displacements(dafa):
    displ = pd.DataFrame()
    #print(len(dafa),len(dafa)*0.1,int(len(dafa)*0.1))
    for i in range(0,int(len(dafa)*0.1)+1,1):
        displ[['dx{:02}'.format(i),'dy{:02}'.format(i)]] = dafa[['x','y']] - dafa[['x','y']].shift(i)
    return displ

def msdcalc(displ):
    sqdispl = pd.DataFrame()
    
    for col in displ.columns:
        if col[1] == 'x':
            sqdispl['d'+col[2:]] = displ['dx'+col[2:]]**2 + displ['dy'+col[2:]]**2

    msd = pd.DataFrame()
    msd['msd'] = sqdispl.mean()
    msd['stderr'] = sqdispl.std()/np.sqrt(sqdispl.count())
    msd['timelag'] = range(len(sqdispl.mean()))

    return msd

def testingArea():
    #infi = "foundTrack.txt"
    infi = "simulatedTracks.txt"
    print("Hello World!")

    print("Read Tracks!")
    df = readTracks(infi)

    print("Make Combined Tracks!")
    ctracks = combineTracks(df)

    '''
    for elem in df['particle_id'].unique():
        plt.plot(df[df['particle_id']==elem]['x'],df[df['particle_id']==elem]['y'])
    plt.show()

    ctracks.plot('x','y')
    plt.show()
    '''

    print("Make Displacements!")
    displcomb = displacements(ctracks)
    displcomb.to_csv("combinedDisplacements.csv",index=False)
    displcomb.hist(bins=50)
    plt.show()

    print("Make MSD!")
    msdcomb = msdcalc(displcomb)
    msdcomb.to_csv("combinedMSD.csv",index=True)
    msdcomb.plot('timelag','msd',yerr='stderr')
    plt.show()



    '''
    dispcolumns = displcomb.columns


    fig, axes = plt.subplots(ncols=2,nrows=1)
    counter = 0

    for elem in dispcolumns:
        displcomb[elem].hist(bins=50,range=(-50,50),ax=axes[counter % 2],histtype='step')
        counter += 1
    plt.show()

    fig, axes = plt.subplots(ncols=2,nrows=1)
    heights = []
    bins = []
    counter = 0
    for elem in dispcolumns:
        if counter == 0:
            h, b = np.histogram(displcomb[elem],bins=50,range=(-50,50))
        else:
            h, b = np.histogram(displcomb[elem],bins=b,range=(-50,50))
        width = (b[1]-b[0])/2
        axes[counter % 2].plot(b[:-1]+width, h)
        counter += 1
    plt.show()
    '''

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

