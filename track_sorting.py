import AnalysisTools.ana_singlestate_legacy as ana
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

def maxDisplacement(track):
    df_track = pd.DataFrame(track)
    df_track.columns=['time','x','y','wx','wy','B','A','SNR','Vol']
    reltrack = df_track - df_track.loc[0]
    return np.sqrt(reltrack['x']**2 + reltrack['y']**2).max()

def maxRelStep(track):
    displ = ana.relativeStpng(track)
    df_rel = pd.DataFrame(displ,columns=['dt','dx','dy'])
    df_rel = df_rel[df_rel['dt']==1]
    d = np.sqrt(df_rel['dx']**2 + df_rel['dy']**2)*0.067
    dh = np.histogram(d,bins=50)
    #plt.plot((dh[1][1:]+dh[1][:-1])/2,dh[0])
    #plt.show()
    return np.sqrt(df_rel['dx']**2 + df_rel['dy']**2).max()
     

def excludeStationary(filename,bins,ran):
    tracks = ana.readTracks(filename)
    print(tracks[0][0])
    displ = []
    relstep = []
    relPos = []
    for tr in tracks:
        if len(tr) < 100:
            continue
        displ.append(maxDisplacement(tr)*0.067)
        relstep.append(maxRelStep(tr)*0.067)
    displhist = np.histogram(displ,bins=bins[0],range=[ran[0]*10,ran[1]*10],density=True)
    relstephist = np.histogram(relstep,bins=bins[1],range=ran,density=True)
    return displhist , relstephist

simfile = "/home/markus/Desktop/TestFiles/Cel5A-23-1.txt"
trackedfile = "/home/markus/Desktop/TestFiles/Cel5A-45-1.txt"

binran = [0,0.08]
simhist,simrelhist = excludeStationary(simfile,bins=[10,10],ran=binran)
trackhist,trackrelhist = excludeStationary(trackedfile,bins=[simhist[1],simrelhist[1]],ran=binran)

xransim = (simhist[1][1:] + simhist[1][:-1])/2
xrantrack = (trackhist[1][1:] + trackhist[1][:-1])/2

plt.figure()
plt.subplot(121)
plt.plot(xransim,simhist[0],'o',label='23')
plt.plot(xrantrack,trackhist[0],'o',label='45')
plt.legend()

xransim = (simrelhist[1][1:] + simrelhist[1][:-1])/2
xrantrack = (trackrelhist[1][1:] + trackrelhist[1][:-1])/2
plt.subplot(122)
plt.plot(xransim,simrelhist[0],'o',label='23')
plt.plot(xrantrack,trackrelhist[0],'o',label='45')
plt.legend()
plt.show()

