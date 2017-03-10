#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2015-11-30
# email: markus.m.rose@gmail.com
#=====================================


import numpy as np
import math
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
import os


#========================================
# User Input Variables
#========================================
Cel="9A"
SR=3

frametime = 1
pixelsize = 0.067
Dfactor = pixelsize*pixelsize/frametime

bCleanUpTracks = True
bSingleTrackEndToEnd = True
bSingleTrackMSDanalysis = True
bCombineTrack = True

#combined Track input
lenMSD_ct = 1000
plotlen = 5 #gives the range of the distribution plots
numberofbins = 50

path = "/media/markus/DataPartition/Cellulases-Analysis_2017-03-10/"
infilename = "foundTrackscomb.txt"
infilename = "tracksCel{:}-SR3_2017-03-06.txt".format(Cel)

#single track analysis input
minTrLength = 100

#debugging variables:
testing = False

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
        track.append(np.array(map(float,line.split()[0:-1])))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    return tracks

def cleanTracksFile(tracks):
    outfile = open("cleandTracks.txt",'w')
    head = ["frame","x","y","width_x","width_y","height","amplitude","sn","volume"]
    printMultiArrayToFile(tracks,outfile,head=head)
    return

def relativeStpng(track):
    relstpng = []

    for i in xrange(1,len(track),1):
        saver = []
        for j in xrange(3):
            saver.append(track[i][j] - track[i-1][j])
        relstpng.append(np.array(saver))

    return np.array(relstpng)

def r2distro(relstpng):
    r2 = []
    for i in xrange(min(20,len(relstpng))):
        saver = []
        for j in xrange(len(relstpng)-i):
            dx = 0
            dy = 0
            for k in xrange(i+1):
                dx += relstpng[j+k][1]/relstpng[j+k][0]
                dy += relstpng[j+k][2]/relstpng[j+k][0]
            saver.append(dx**2+dy**2)
        r2.append(np.array(saver))
    return r2


def displacementDistro(relstpng):
    displ = []
    for i in xrange(min(20,len(relstpng))):
        saver = []
        for j in xrange(len(relstpng)-i):
            dx = 0
            dy = 0
            for k in xrange(i+1):
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

    for n in xrange(1,l,1):
        msdsave = 0
        possave = []

        for i in xrange(len(track)):
            for j in xrange(i+1,len(track)):
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

def plotTrack(track,title="Track",save=True):
    plt.plot(track[1],track[2],'k')
    plt.xlabel("x [px]")
    plt.ylabel("y [px]")
    if save:
        plt.savefig(title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    plt.show()
    return
    
def plotMSD(msd,D,title="Mean-Squared-Displacement",save=True,labelname="labelname"):
    plt.plot(msd[:,0],msd[:,1],'ro')
    ran = np.arange(msd[-1,0])
    plt.plot(ran,4*D*ran,'k',label=labelname)
    plt.xlabel("time lag [s]")
    plt.ylabel("MSD [um^2/s]")
    if save:
        plt.savefig(title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    plt.legend()
    plt.show()

def plotDistro(distro,xlabel,title,save=True):
    dbox = distro[1][1] - distro[1][0]
    xran = distro
    print xran
    plt.plot(distro[1][:-1]+dbox*0.5,distro[0],'k')
    plt.xlabel(xlabel)
    plt.ylabel("Normalized counts")
    if save:
        plt.savefig(title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    plt.show()
    return

def plotMultidistro(distarray,xlabel,title,save=True):
    for elem in distarray:
        dbox = elem[1][1]-elem[1][0]
        plt.plot(elem[1][:-1]+dbox*0.5,elem[0],'o')
    plt.xlabel(xlabel)
    plt.ylabel("Normalized counts")
    if save:
        plt.savefig(title+"-plot.png",format="png", dpi=600)
    plt.title(title)
    plt.show()
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
    tlTs = range(10)
    for i in xrange(10,len(tracks)):
        c = 0
        while (c < 10) and (len(tracks[i]) > len(tracks[tlTs[c]])):
            c += 1
        tlTs.insert(c,i)
        del tlTs[0]
    return tlTs
        
def tenMediumTracks(tracks):
    tmtl = []
    for i in xrange(len(tracks)):
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
def eedispllist(tracks):
    eedispl2 = map(endToEnd2,tracks)
    eedispl = np.sqrt(eedispl2)
    print "Analyzing the End-To-End distribution of " + str(len(tracks)) + " tracks."
    histo = np.histogram(eedispl,bins=numberofbins,range=(0,10),density=True)
    plt.plot(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'ro',histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'-')
    #plt.axis([0,3,0,1])
    plt.title("End-To-End Track Length Distribution")
    plt.ylabel("relative Counts")
    plt.xlabel("End to end displacement (pixel)")
    plt.xscale('log')
    #plt.axis([0.05,12,0,1])
    plt.savefig('EndToEndDistrib.png', format='png', dpi=600)
    plt.show()

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open("end2EndDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["displacement(pixel)","relativeCounts"])
    print "End-To-End Displacement has been saved to folder."
    return histo
    

def diffConstDistrib(tracks):

    print "Starting Analysis of " + str(len(tracks)) + " single tracks."
    print "....This will take a while..."
    print "........(creating a list of MSD from all tracks; this takes long...)"
    msdlist = map(msd,tracks)
    print "........(finding diffusion coefficient from all MSDs from list)"
    Dlist = findDiffConsts(msdlist)
    print ">>>> The average diffusion coefficient is: " + str(Dlist.mean()*Dfactor) + " +- " + str(Dlist.std()*Dfactor) + " um^2/s"
    print "........(finding the lengths of the single tracks)"
    lenList= np.array(map(len,tracks))
    print ">>>> The average track length is: " + str(lenList.mean()*frametime) + " +- " + str(lenList.std()*frametime) + " s"
    print "Showing: Diffusion coefficient distribution of " + str(len(tracks)) + " tracks."
    histo = np.histogram(Dlist,bins=numberofbins,density=True)
    plt.plot(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'ro',label="{:} +- {:} um^2/s".format(Dlist.mean()*Dfactor,Dlist.std()*Dfactor))
    #plt.axis([0,10,0,1])
    plt.title("Diffusion Coefficient Distribution")
    plt.ylabel("relative Counts")
    plt.xlabel("Diffusion Constants (px^2*framerate)")
    plt.legend()
    plt.savefig('DiffConstDistrib.png', format='png', dpi=600)
    plt.show()
    

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open("diffConstDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["diffConst(pixel**2/frame)","relativeCounts"])
    
    print "Showing: Length of tracks distribution for " + str(len(tracks)) + " tracks."
    lenhist = np.histogram(lenList,bins=numberofbins,density=True)
    plt.plot(lenhist[1][1:]-(lenhist[1][1]-lenhist[1][0])/2,lenhist[0],'ro')
    #plt.axis([0,30,0,1])
    plt.title("Length Distribution of single tracks")
    plt.ylabel("relative Counts")
    plt.xlabel("Track length (frames)")
    plt.savefig('lengthDistribution.png', format='png', dpi=600)
    plt.show()
    outarray = np.array([lenhist[1][1:]-(lenhist[1][1]-lenhist[1][0])/2,lenhist[0]]).transpose()
    fo = open("lengthDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(frame)","relativeCounts"])

    print "Showing: Dependence of the diffusion coefficient on the track length of " + str(len(tracks)) + " individual tracks."
    nubin = 30
    wbin = (lenhist[1][-1]-lenhist[1][0])/nubin
    bincount = 1
    Dmean = np.zeros((3,nubin))
    Dmean[0] = np.arange(nubin)*wbin+wbin/2+lenhist[1][0]
    for i in xrange(len(Dlist)):
        bincount = 1
        while Dlist[i,0] > bincount * wbin+lenhist[1][0]:
            bincount+=1
            if bincount > nubin:
                print "Oh no, yes"
                bincount -= 1
                break
        Dmean[1,bincount-1] += 1
        Dmean[2,bincount-1] += Dlist[i,1]
    for i in xrange(len(Dmean[0])):
        if Dmean[1,i] == 0:
            continue
        Dmean[2,i] = Dmean[2,i]/Dmean[1,i]
    
    plt.plot(Dmean[0],Dmean[2],'ro')
    plt.title("Dependence of the diffusion coefficient on the track length")
    plt.ylabel("averaged diffusion constant (px^2*framerate")
    plt.xlabel("Track length (frames)")
    plt.savefig('trLengthDiffConstDependence.png', format='png', dpi=600)
    plt.show()
    outarray = np.array([Dmean[0],Dmean[2]]).transpose()
    fo = open("Length-Diffconst-Relation.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(frame)","meanDiffConst"])
    return histo
#=======================================



#=== Combined Tracks analysis =================
def combineTracks(tracks):
    lastpart = np.zeros((len(tracks[0][0])))
    combtr = [np.array(lastpart)]
    for tr in tracks:
        lastpart = np.array(combtr[-1])
        for part in xrange(1,len(tr),1):
            outpart = []
            for i in xrange(len(tr[0])):
                if i < 3:
                    outpart.append(tr[part][i] - tr[0][i]+lastpart[i])
                else:
                    outpart.append(tr[part][i])
            combtr.append(np.array(outpart))
    outfile = open("combinedTrack.txt",'w')
    head = ["Step","x","y","widthx","widthy","height","amplitude","sn","volume"]
    printArrayToFile(combtr,outfile,head)
    return np.array(combtr)




def analyzeCombinedTrack(tracks,lenMSD=500):
    print "Combining " + str(len(tracks)) + " tracks."
    ct = combineTracks(tracks)
    plotTrack(ct.transpose())
    print "Creating MSD for combined track."
    ct_msd = msd(ct,length=lenMSD)
    ct_diffconst = findDiffConsts([ct_msd])[0]
    print ">>>> Found diffusion coefficient: " + str(ct_diffconst[1]*Dfactor) + " um^2/s"
    of = open("MSD-combinedTrack.txt",'w')
    printArrayToFile(ct_msd,of,head=["Stpngize","MSD"])
    plotMSD(ct_msd,ct_diffconst[1],labelname="{:} um^2/s".format(ct_diffconst[1]*Dfactor))
    print "Starting Distribution Analysis"
    distributionAnalysis(ct,plotlen)
    return ct_diffconst

def distributionAnalysis(track,plotlen):
    dipllist = relativeStpng(track)
    print "....Saving Displacements to file."
    outfile = open("combinedTrack-relativeXYDisplacements.txt",'w')
    printArrayToFile(dipllist,outfile,["Steppingtime","dx","dy"])
    
    print "....Creating r^2-distribution"
    r2 = r2distro(dipllist)
    histograms = []
    counter = 0
    for elr2 in r2:
        histo = np.histogram(elr2,bins=numberofbins,range=(0,plotlen),density=True)
        counter += 1
        histograms.append(list(histo))
    plotMultidistro([histograms[i] for i in [0,4,8,16]],xlabel="r^2 [px^2]",title="r2-Distribution-combTr")
    
    print "....Creating distribution of stpngizes in x and y"
    dispdist = displacementDistro(dipllist)
    histograms = []
    counter = 0
    for elr2 in dispdist:
        histo = np.histogram(elr2,bins=numberofbins,range=(-plotlen,plotlen),density=True)
        counter += 1
        histograms.append(list(histo))
    plotMultidistro([histograms[i] for i in [0,4,8,16]],xlabel="dx and dy [px]",title="xy-Distribution-combTr")
    return
    
#===========================================



#====== Test new functions here ==================
def testfunctions():
    tracks = readTracks("foundTracks.txt")
    ct = combineTracks(tracks)
    distributionAnalysis(ct,plotlen)

    return
#================================================



#====================================
#The big MAIN
#====================================
def main():
    
    if (not bSingleTrackEndToEnd) and (not bSingleTrackMSDanalysis) and (not bCombineTrack):
        return

    os.chdir(path)
    
    tracks = readTracks(infilename)

    spng = os.path.join(path,"Tracks-Cel{:}-SR{:}".format(Cel,SR),"SingleStateAnalysis")
    if not os.path.isdir(spng):
        os.mkdir(spng)
    os.chdir(spng)

    
    if bCleanUpTracks:
        print
        print "Cleaning Track File from NAN"
        print "----------------------------"
        cleanTracksFile(tracks)
    
    considered = []
    for i in tracks:
        if len(i) >= minTrLength:
            considered.append(i)
    if len(considered) == 0:
        print "Tracks are too short! Please adjust 'minTrackLen' to a lower value!"
        raw_input("Please restart again...")
        return
    if bSingleTrackEndToEnd:
        print
        print
        print "Starting End-To-End Displacement Analysis for single tracks"
        print "-----------------------------------------------------------"
        eehisto = eedispllist(considered)
    if len(considered) > 100:
        considered = considered[:100]
    
    if bSingleTrackMSDanalysis:
        print
        print
        print "Starting Diffusion Constant Analysis for single tracks"
        print "------------------------------------------------------"
        diffChisto = diffConstDistrib(considered)
    if bCombineTrack:
        print
        print
        print "Starting Combined Track Analysis"
        print "--------------------------------"
        analyzeCombinedTrack(considered,lenMSD=lenMSD_ct)
    raw_input("Press Enter to finish...")
    return
#=====================================



if __name__ == "__main__":
    if testing:
        testfunctions()
    else:
        main()



#=== unused =======================
def minimumEndToEnd(tracks):
    minEE = []
    for i in xrange(len(tracks)):
        if endToEnd2(tracks[i]) > 400:
            minEE.append([i,endToEnd2(tracks[i])])
    return minEE


def oldmain(tracks):
    tlt =  tenLongTracks(tracks)
    tmtl = tenMediumTracks(tracks)
    print tlt, map(len,[tracks[x] for x in tlt])
    #print tmtl, map(len,[tracks[x] for x in tmtl])
    
    subTracks = [tracks[i] for i in tlt]
    minEE = minimumEndToEnd(subTracks)
    print minEE
    allmsds = map(msd,tracks[:])
    alldiffs = findDiffConsts(allmsds)
    print "Mean of all tracks: " + str(alldiffs.mean()) + " +- " + str(alldiffs.std())
    allmsds = []
    for i in xrange(len(subTracks)):
        allmsds.append(msd(subTracks[i]))

    alldiffs = findDiffConsts(allmsds)
    print alldiffs.mean()

    numtra = np.arange(len(subTracks))
    firstmsd = map(msd,[subTracks[int(k)] for k in numtra])
    diffconstant = findDiffConsts(firstmsd)
    print diffconstant


    for i in xrange(len(subTracks)):
        plotTrack(subTracks[i])
        plotMSD(firstmsd[i],diffconstant[i][1])

    
    fo = open("allMSD.txt",'w')
    head = ["FrameStpng","MSD","err(MSD)"]
    printMultiArrayToFile(allmsds,fo,sepword="MSD",head=head)
#===============================================

