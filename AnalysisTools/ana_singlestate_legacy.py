#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2015-11-30
# email: markus.m.rose@gmail.com
#=====================================


import numpy as np
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
#++++++++++++++++++++++++++++++++++++++++

'''
basic functions: Read in tracks, MSD, r^2-distribution, xy-stpngize-distribution
'''

#read in Tracks
def readTracks(infile):
    fopen = open(infile,'r')

    tracks = []
    track = []
    brt = False

    for line in fopen:

        if len(line.strip()) == 0:
            if brt:
                brt = False
                tracks.append(np.array(track))
                del track
            continue
        elif line[0] == '#':
            if not brt:
                brt = True
                track = []
            continue
        track.append(np.array(list(map(float,line.split()[0:-1]))))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    return tracks

def cleanTracksFile(tracks,output="cleanedTracks.txt"):
    outfile = open(output,'w')
    head = ["frame","x","y","width_x","width_y","height","amplitude","sn","volume"]
    printMultiArrayToFile(tracks,outfile,head=head)
    return

def relativeStpng(track):
    relstpng = []

    for i in range(1,len(track),1):
        saver = []
        for j in range(3):
            saver.append(track[i][j] - track[i-1][j])
        relstpng.append(np.array(saver))

    return np.array(relstpng)

def r2distro(relstpng):
    r2 = []
    for i in range(min(20,len(relstpng))):
        saver = []
        for j in range(len(relstpng)-i):
            dx = 0
            dy = 0
            for k in range(i+1):
                dx += relstpng[j+k][1]/relstpng[j+k][0]
                dy += relstpng[j+k][2]/relstpng[j+k][0]
            saver.append(dx**2+dy**2)
        r2.append(np.array(saver))
    return r2


def displacementDistro(relstpng):
    displ = []
    for i in range(min(20,len(relstpng))):
        saver = []
        for j in range(len(relstpng)-i):
            dx = 0
            dy = 0
            for k in range(i+1):
                dx += relstpng[j+k][1]/relstpng[j+k][0]
                dy += relstpng[j+k][2]/relstpng[j+k][0]
            saver.append(dx)
            saver.append(dy)
        displ.append(np.array(saver))
    return displ


    
def msd(track,length=500):
    msd = []
    l = length + 1
    if l > len(track):
        l = len(track)

    for n in range(1,l,1):
        msdsave = 0
        possave = []

        for i in range(len(track)):
            for j in range(i+1,len(track)):
                dt = track[j,0] - track[i,0]

                if dt < n:
                    continue
                elif dt > n:
                    break
                else:
                    possave.append([i,j])
                    dx = track[j,1] - track[i,1]
                    dy = track[j,2] - track[i,2]
                    msdsave += dx**2 + dy**2

        if msdsave == 0:
            continue

        msd.append(np.zeros((3)))
        msd[-1][0] = n
        msd[-1][1] = msdsave / len(possave)
        
        if len(possave) > 1:
            errmsd = 0
            for pos in possave:
                dx = track[pos[1],1] - track[pos[0],1]
                dy = track[pos[1],2] - track[pos[0],2]
                errmsd += (dx**2 + dy**2 - msd[-1][1])**2
        
            msd[-1][2] = math.sqrt(errmsd/((len(possave)-1)*len(possave)))
        else:
            msd[-1][2] = 0
        
    return np.array(msd)

#====================================
'''Print Arrays to files and show plots'''
def printArrayToFile(arr,fopen,head=None):
    if head != None:
        fopen.write("#")
        for word in head:
            fopen.write("{} ".format(word))
        fopen.write('\n')
    for line in arr:
        for elem in line:
            fopen.write("{} ".format(elem))
        fopen.write("\n")

def printMultiArrayToFile(arr,fopen,sepword="Track",head=None):
    counter = 0
    for mem in arr:
        counter += 1
        fopen.write("# {} {}: -------------------\n".format(sepword,counter))
        printArrayToFile(mem,fopen,head=head)
        fopen.write("\n\n")

def plotTrack(track,title="Track",save=True,path='.'):
    plt.plot(track[1],track[2],'k')
    plt.xlabel("x [px]")
    plt.ylabel("y [px]")
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    #plt.show()
    plt.close()
    return
    
def plotMSD(msd,D,title="Mean-Squared-Displacement",save=True,labelname="labelname",path='.'):
    plt.plot(msd[:,0],msd[:,1],'ro')
    ran = np.arange(msd[-1,0])
    plt.plot(ran,4*D*ran,'k',label=labelname)
    plt.xlabel("Lag Time [s]")
    plt.ylabel(r"MSD [um$^2$/s]")
    plt.legend()
    plt.title(title)
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=600)
    #plt.show()
    plt.close()
    return

def plotDistro(distro,xlabel,title,save=True,path='.'):
    dbox = distro[1][1] - distro[1][0]
    xran = distro
    print(xran)
    plt.bar(distro[1][:-1]+dbox*0.5,distro[0],width=dbox)
    plt.xlabel(xlabel)
    plt.ylabel("Counts")
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    #plt.show()
    plt.close()
    return

def plotMultidistro(distarray,xlabel,title,save=True,path='.',bar=True):
    for elem in distarray:
        dbox = elem[1][1]-elem[1][0]
        if bar:
            plt.bar(elem[1][:-1]+dbox*0.5,elem[0],width=dbox)
        else:
            plt.plot(elem[1][:-1]+dbox*0.5,elem[0],'o')
    plt.xlabel(xlabel)
    plt.ylabel("Counts")
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    #plt.show()
    plt.close()
    return

#=====================================

def linfun(x,D):
    return 4*D*x

def fitArray(msd,area=1):
    if area > 1:
        area = 1
    #print len(msd)
    xdata = msd[0:int(len(msd)*area),0]
    ydata = msd[0:int(len(msd)*area),1]
    iniguess = [1]

    popt, pcov = curve_fit(linfun, xdata, ydata, iniguess)
    return popt


def findDiffConsts(msd):
    diffC = []
    counter = 0
    for elem in msd:
        counter += 1
        #print "Track {}".format(counter)
        if len(elem) == 0:
            counter -= 1
            continue
        if True:
            diffC.append(np.array([len(elem),fitArray(elem)]))
        else:
            diffC.append(np.array([len(elem),fitArray(elem,area=0.3)]))
    
    return np.array(diffC)

#==== Helper functions =====================
def tenLongTracks(tracks):
    tlTs = list(range(10))
    for i in range(10,len(tracks)):
        c = 0
        while (c < 10) and (len(tracks[i]) > len(tracks[tlTs[c]])):
            c += 1
        tlTs.insert(c,i)
        del tlTs[0]
    return tlTs
        
def tenMediumTracks(tracks):
    tmtl = []
    for i in range(len(tracks)):
        if len(tracks[i]) >=10 and len(tracks[i])<20:
            tmtl.append(i)
        #if len(tmtl) > 10:
        #    break
    return tmtl


def endToEnd2(track):
    if len(track) == 1:
        return 0
    dx = track[-1,1]-track[0,1]
    dy = track[-1,2]-track[0,2]
    return dx**2+dy**2
#=============================================




#=== Single Track Analysis ==============
def eedispllist(tracks,numberofbins=50,path='.'):
    eedispl2 = list(map(endToEnd2,tracks))
    eedispl = np.sqrt(eedispl2)
    print(("Analyzing the End-To-End distribution of " + str(len(tracks)) + " tracks."))
    histo = np.histogram(eedispl,bins=numberofbins,range=(0,10),density=False)
    plt.plot(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'ro',histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'-')
    #plt.axis([0,3,0,1])
    plt.title("End-To-End Track Length Distribution")
    plt.ylabel("Counts")
    plt.xlabel("End to end displacement (pixel)")
    plt.xscale('log')
    #plt.axis([0.05,12,0,1])
    plt.savefig(path+'/EndToEndDistrib.png', format='png', dpi=600)
    #plt.show()
    plt.close()

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open(path+"/end2EndDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["displacement(pixel)","Counts"])
    print("End-To-End Displacement has been saved to folder.")
    return histo
    

def diffConstDistrib(tracks,pixelsize,frametime,Dfactor,numberofbins=50,path='.'):

    print(("Starting Analysis of " + str(len(tracks)) + " single tracks."))
    print("....This will take a while...")
    print("........(creating a list of MSD from all tracks; this takes long...)")
    msdlist = list(map(msd,tracks))
    print("........(finding diffusion coefficient from all MSDs from list)")
    Dlist = findDiffConsts(msdlist)
    print((">>>> The average diffusion coefficient is: " + str(Dlist.mean()*Dfactor) + " +- " + str(Dlist.std()*Dfactor) + " um^2/s"))
    print("........(finding the lengths of the single tracks)")
    lenList= np.array(list(map(len,tracks)))
    print((">>>> The average track length is: " + str(lenList.mean()*frametime) + " +- " + str(lenList.std()*frametime) + " s"))
    print(("Showing: Diffusion coefficient distribution of " + str(len(tracks)) + " tracks."))
    histo = np.histogram(Dlist,bins=numberofbins,density=False)
    width = (histo[1][1]-histo[1][0])/2
    plt.bar(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],width=width,label=r"{:} +- {:} $\mu$m$^2$/s".format(Dlist.mean()*Dfactor,Dlist.std()*Dfactor))
    #plt.axis([0,10,0,1])
    plt.title("Diffusion Coefficient Distribution")
    plt.ylabel("Counts")
    plt.xlabel(r"Diffusion Constants (px$^2$*framerate)")
    plt.legend()
    plt.savefig(path+'/DiffConstDistrib.png', format='png', dpi=600)
    #plt.show()
    plt.close()
    

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open(path+"/diffConstDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["diffConst(pixel**2/frame)","Counts"])
    
    print(("Showing: Length of tracks distribution for " + str(len(tracks)) + " tracks."))
    lenhist = np.histogram(lenList,bins=numberofbins,density=False)
    width = (lenhist[1][1]-lenhist[1][0])/2
    plt.bar(lenhist[1][1:]-(lenhist[1][1]-lenhist[1][0])/2,lenhist[0],width=width)
    #plt.axis([0,30,0,1])
    plt.title("Length Distribution of single tracks")
    plt.ylabel("Counts")
    plt.xlabel("Track length (frames)")
    plt.savefig(path+'/lengthDistribution.png', format='png', dpi=600)
    #plt.show()
    plt.close()
    outarray = np.array([lenhist[1][1:]-(lenhist[1][1]-lenhist[1][0])/2,lenhist[0]]).transpose()
    fo = open(path+"/lengthDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(frame)","Counts"])

    print(("Showing: Dependence of the diffusion coefficient on the track length of " + str(len(tracks)) + " individual tracks."))
    nubin = 30
    wbin = (lenhist[1][-1]-lenhist[1][0])/nubin
    bincount = 1
    Dmean = np.zeros((3,nubin))
    Dmean[0] = np.arange(nubin)*wbin+wbin/2+lenhist[1][0]
    for i in range(len(Dlist)):
        bincount = 1
        while Dlist[i,0] > bincount * wbin+lenhist[1][0]:
            bincount+=1
            if bincount > nubin:
                print("Oh no, yes")
                bincount -= 1
                break
        Dmean[1,bincount-1] += 1
        Dmean[2,bincount-1] += Dlist[i,1]
    for i in range(len(Dmean[0])):
        if Dmean[1,i] == 0:
            continue
        Dmean[2,i] = Dmean[2,i]/Dmean[1,i]
    
    plt.plot(Dmean[0],Dmean[2],'ro')
    plt.title("Dependence of the diffusion coefficient on the track length")
    plt.ylabel(r"averaged diffusion constant (px$^2$*framerate")
    plt.xlabel("Track length (frames)")
    plt.savefig(path+'/trLengthDiffConstDependence.png', format='png', dpi=600)
    #plt.show()
    plt.close()
    outarray = np.array([Dmean[0],Dmean[2]]).transpose()
    fo = open(path+"/Length-Diffconst-Relation.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(frame)","meanDiffConst"])
    return histo
#=======================================



#=== Combined Tracks analysis =================
def combineTracks(tracks,path='.'):
    lastpart = np.zeros((len(tracks[0][0])))
    combtr = [np.array(lastpart)]
    for tr in tracks:
        lastpart = np.array(combtr[-1])
        for part in range(1,len(tr),1):
            outpart = []
            for i in range(len(tr[0])):
                if i < 3:
                    outpart.append(tr[part][i] - tr[0][i]+lastpart[i])
                else:
                    outpart.append(tr[part][i])
            combtr.append(np.array(outpart))
    outfile = open(path+"/combinedTrack.txt",'w')
    head = ["Step","x","y","widthx","widthy","height","amplitude","sn","volume"]
    printArrayToFile(combtr,outfile,head)
    return np.array(combtr)




def analyzeCombinedTrack(tracks,pixelsize,frametime,Dfactor,lenMSD=500,numberofbins=50,plotlen=30,path='.'):
    print(("Combining " + str(len(tracks)) + " tracks."))
    ct = combineTracks(tracks,path=path)
    plotTrack(ct.transpose(),path=path)
    print("Creating MSD for combined track.")
    lenMSD = min(lenMSD,int(len(ct)*0.2))
    ct_msd = msd(ct,length=lenMSD)
    ct_diffconst = findDiffConsts([ct_msd])[0]
    print((">>>> Found diffusion coefficient: " + str(ct_diffconst[1]*Dfactor) + " um^2/s"))
    of = open(path+"/MSD-combinedTrack.txt",'w')
    printArrayToFile(ct_msd,of,head=["Stpngize","MSD"])
    plotMSD(ct_msd,ct_diffconst[1],labelname=r"{:} $\mu$m$^2$/s".format(ct_diffconst[1]*Dfactor),path=path)
    print("Starting Distribution Analysis")
    distributionAnalysis(ct,pixelsize,frametime,Dfactor,plotlen,numberofbins=numberofbins,path=path)
    return ct_diffconst

def distributionAnalysis(track,pixelsize,frametime,Dfactor,plotlen,numberofbins=50,path='.'):
    dipllist = relativeStpng(track)
    print("....Saving Displacements to file.")
    outfile = open(path+"/combinedTrack-relativeXYDisplacements.txt",'w')
    printArrayToFile(dipllist,outfile,["Steppingtime","dx","dy"])
    
    print("....Creating r^2-distribution")
    r2 = r2distro(dipllist)
    histograms = []
    counter = 0
    for elr2 in r2:
        histo = np.histogram(elr2*pixelsize**2,bins=numberofbins,range=(0,plotlen*pixelsize**2),density=False)
        counter += 1
        histograms.append(list(histo))
    plotMultidistro([histograms[i] for i in [0,4,8,16]],xlabel=r"$r^2$ Distribution [$\mu$m$^2$]",title="r2-Distribution-combTr",path=path,bar=False)
    
    print("....Creating distribution of stpngizes in x and y")
    dispdist = displacementDistro(dipllist)
    histograms = []
    counter = 0
    for elr2 in dispdist:
        histo = np.histogram(elr2*pixelsize,bins=numberofbins,range=(-plotlen*pixelsize,plotlen*pixelsize),density=False)
        counter += 1
        histograms.append(list(histo))
    plotMultidistro([histograms[i] for i in [0,4,8,16]],xlabel=r"dx and dy [$\mu$m]",title="xy-Distribution-combTr",path=path,bar=False)
    return
    
#===========================================


#====================================
#The big MAIN
#====================================
def doAnalysis(trackfile,pixelsize=0.100,frametime=0.1,bCleanUpTracks=True,bSingleTrackEndToEnd=False,bSingleTrackMSDanalysis=True,bCombineTrack=True):
    #plotting parameters
    Dfactor = pixelsize*pixelsize/frametime

    lenMSD_ct = 300
    plotlen = 30 #gives the range of the distribution plots
    numberofbins = 70
    small = 20
    large = 100

    #single track analysis input
    minTrLength = 2
    
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
        sys.stdout.flush()
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
    sys.stdout.flush()
    return
#=====================================



if __name__ == "__main__":
    trackfile = '/home/markus/Desktop/TestFiles/Analysis/foundTracks.txt'
    doAnalysis(trackfile,pixelsize=0.100,frametime=0.1,bCleanUpTracks=True,bSingleTrackEndToEnd=True,bSingleTrackMSDanalysis=True,bCombineTrack=True)



#=== unused =======================
def minimumEndToEnd(tracks):
    minEE = []
    for i in range(len(tracks)):
        if endToEnd2(tracks[i]) > 400:
            minEE.append([i,endToEnd2(tracks[i])])
    return minEE
#==================================


