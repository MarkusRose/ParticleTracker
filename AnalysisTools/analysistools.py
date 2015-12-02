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


#========================================
# User Input Variables
#========================================

bCleanUpTracks = True
bSingleTrackEndToEnd = True
bSingleTrackMSDanalysis = True
bCombineTrack = True

#combined Track input
lenMSD_ct = 25
plotlen = 5 #gives the range of the distribution plots


#single track analysis input
minTrLength = 1

#debugging variables:
testing = False

#========================================
# Program functions
#========================================
#++++++++++++++++++++++++++++++++++++++++

'''
basic functions: Read in tracks, MSD, r^2-distribution, xy-stepsize-distribution
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
        track.append(np.array(map(float,line.split())))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    return tracks

def cleanTracksFile(tracks):
    outfile = open("cleandTracks.txt",'w')
    head = ["frame","x","y","width_x","width_y","height","amplitude","sn","volume"]
    printMultiArrayToFile(tracks,outfile,head=head)
    return

def relativeSteps(track):
    relsteps = []

    for i in xrange(1,len(track),1):
        saver = []
        for j in xrange(3):
            saver.append(track[i][j] - track[i-1][j])
        relsteps.append(np.array(saver))

    return np.array(relsteps)

def r2distro(relsteps):
    r2 = []
    for i in xrange(min(20,len(relsteps))):
        saver = []
        for j in xrange(len(relsteps)-i):
            dx = 0
            dy = 0
            for k in xrange(i+1):
                dx += relsteps[j+k][1]/relsteps[j+k][0]
                dy += relsteps[j+k][2]/relsteps[j+k][0]
            saver.append(dx**2+dy**2)
        r2.append(np.array(saver))
    return r2


def displacementDistro(relsteps):
    displ = []
    for i in xrange(min(20,len(relsteps))):
        saver = []
        for j in xrange(len(relsteps)-i):
            dx = 0
            dy = 0
            for k in xrange(i+1):
                dx += relsteps[j+k][1]/relsteps[j+k][0]
                dy += relsteps[j+k][2]/relsteps[j+k][0]
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

def plotTrack(track,title="Track",save=False):
    plt.plot(track[1],track[2],'k')
    plt.xlabel("x [px]")
    plt.ylabel("y [px]")
    if save:
        plt.savefig(title+"-plot.eps",format="eps", dpi=600)
    plt.title(title)
    plt.show()
    return
    
def plotMSD(msd,D,title="Mean-Squared-Displacement",save=False):
    plt.plot(msd[:,0],msd[:,1],'ro')
    ran = np.arange(msd[-1,0])
    plt.plot(ran,4*D*ran,'k')
    plt.xlabel("time lag [frameinterval]")
    plt.ylabel("MSD [px^2/frameinterval]")
    if save:
        plt.savefig(title+"-plot.eps",format="eps", dpi=600)
    plt.title(title)
    plt.show()

def plotDistro(distro,xlabel,title,save=False):
    dbox = distro[1][1] - distro[1][0]
    xran = distro
    print xran
    plt.plot(distro[1][:-1]+dbox*0.5,distro[0],'k')
    plt.xlabel(xlabel)
    plt.ylabel("Normalized counts")
    if save:
        plt.savefig(title+"-plot.eps",format="eps", dpi=600)
    plt.title(title)
    plt.show()
    return

def plotMultidistro(distarray,xlabel,title,save=False):
    for elem in distarray:
        dbox = elem[1][1]-elem[1][0]
        plt.plot(elem[1][:-1]+dbox*0.5,elem[0],'o')
    plt.xlabel(xlabel)
    plt.ylabel("Normalized counts")
    if save:
        plt.savefig(title+"-plot.eps",format="eps", dpi=600)
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
    print eedispl2
    eedispl = np.sqrt(eedispl2)
    print "Analyzing the End-To-End distribution of " + str(len(tracks)) + " tracks."
    histo = np.histogram(eedispl,bins=100,density=True)
    plt.plot(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'ro')
    #plt.axis([0,3,0,1])
    plt.title("End-To-End Track Length Distribution")
    plt.ylabel("relative Counts")
    plt.xlabel("End to end displacement (pixel)")
    plt.savefig('EndToEndDistrib.eps', format='eps', dpi=600)
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
    print ">>>> The average diffusion coefficient is: " + str(Dlist.mean()) + " +- " + str(Dlist.std()) + " px^2/frame"
    print "........(finding the lengths of the single tracks)"
    lenList= np.array(map(len,tracks))
    print ">>>> The average track length is: " + str(lenList.mean()) + " +- " + str(lenList.std()) + " px^2/frame"
    print "Showing: Diffusion coefficient distribution of " + str(len(tracks)) + " tracks."
    histo = np.histogram(Dlist,bins=100,range=(0,10),density=True)
    plt.plot(histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0],'ro')
    #plt.axis([0,10,0,1])
    plt.title("Diffusion Coefficient Distribution")
    plt.ylabel("relative Counts")
    plt.xlabel("Diffusion Constants (px^2*framerate)")
    plt.savefig('DiffConstDistrib.eps', format='eps', dpi=600)
    plt.show()
    

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open("diffConstDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["diffConst(pixel**2/frame)","relativeCounts"])
    
    print "Showing: Length of tracks distribution for " + str(len(tracks)) + " tracks."
    lenhist = np.histogram(lenList,bins=100,density=True)
    plt.plot(lenhist[1][1:]-(lenhist[1][1]-lenhist[1][0])/2,lenhist[0],'ro')
    #plt.axis([0,30,0,1])
    plt.title("Length Distribution of single tracks")
    plt.ylabel("relative Counts")
    plt.xlabel("Track length (frames)")
    plt.savefig('lengthDistribution.eps', format='eps', dpi=600)
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
    plt.savefig('trLengthDiffConstDependence.eps', format='eps', dpi=600)
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
    print ">>>> Found diffusion coefficient: " + str(ct_diffconst[1]) + " px^2/frameinterval"
    of = open("MSD-combinedTrack.txt",'w')
    printArrayToFile(ct_msd,of,head=["Stepsize","MSD"])
    plotMSD(ct_msd,ct_diffconst[1])
    print "Starting Distribution Analysis"
    distributionAnalysis(ct,plotlen)
    return ct_diffconst

def distributionAnalysis(track,plotlen):
    dipllist = relativeSteps(track)
    print "....Saving Displacements to file."
    outfile = open("combinedTrack-relativeXYDisplacements.txt",'w')
    printArrayToFile(dipllist,outfile,["Steppingtime","dx","dy"])
    
    print "....Creating r^2-distribution"
    r2 = r2distro(dipllist)
    histograms = []
    counter = 0
    for elr2 in r2:
        histo = np.histogram(elr2,bins=100,range=(0,plotlen),density=True)
        counter += 1
        histograms.append(list(histo))
    plotMultidistro([histograms[i] for i in [0,4,8,16]],xlabel="r^2 [px^2]",title="r2-Distribution-combTr")
    
    print "....Creating distribution of stepsizes in x and y"
    dispdist = displacementDistro(dipllist)
    histograms = []
    counter = 0
    for elr2 in dispdist:
        histo = np.histogram(elr2,bins=100,range=(-plotlen,plotlen),density=True)
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
    
    tracks = readTracks("foundTracks.txt")
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
    if bSingleTrackEndToEnd:
        print
        print
        print "Starting End-To-End Displacement Analysis for single tracks"
        print "-----------------------------------------------------------"
        eehisto = eedispllist(considered)
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
        analyzeCombinedTrack(tracks,lenMSD=lenMSD_ct)
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
    head = ["FrameSteps","MSD","err(MSD)"]
    printMultiArrayToFile(allmsds,fo,sepword="MSD",head=head)
#===============================================

