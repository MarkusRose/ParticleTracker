#=====================================
# Analysis script for a track file
# Author: Markus Rose
# Date: 2015-11-30
# email: rosemm2@mcmaster.ca
#=====================================

import numpy as np
import math
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
import os
from time import strftime

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
    trackids = []

    for line in fopen:

        if len(line.strip()) == 0:
            if brt:
                brt = False
                tracks.append(np.array(track))
                trackids.append(trid)
                del track
            continue
        elif line[0] == '#':
            if not brt:
                brt = True
                track = []
            continue
        track.append(np.array(list(map(float,line.split()[0:-1]))))
        trid = line.split()[-1]

    if len(track) > 0:
        tracks.append(np.array(track))
        trackids.append(trid)
        del track

    return tracks,trackids

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


    
def msd(track,length=300):
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
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=200)
    plt.title(title)
    #plt.show()
    plt.close()
    return
    
def plotMSD(msd,D,xaxisrange,pxsize=1,frametime=1,title="Mean-Squared-Displacement",save=True,labelname="labelname",path='.'):
    mask = msd[:,0] <= xaxisrange
    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111)
    ax.plot(msd[:,0][mask]*frametime,msd[:,1][mask]*pxsize**2,'ro')
    ran = np.arange(msd[-1,0])
    ax.plot(ran*frametime,4*D*ran*pxsize**2,'k',label=labelname)
    ax.set_xlabel("Lag Time [s]")
    ax.set_ylabel(r"MSD [$\mu m^2$]")
    ax.legend()
    ax.set_xlim((0,xaxisrange*frametime))
    ax.set_title(title)
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=200)
    #plt.show()
    plt.close('all')
    return

def plotDistro(distro,xlabel,title,save=True,path='.'):
    dbox = distro[1][1] - distro[1][0]
    xran = distro
    print(xran)
    plt.bar(distro[1][:-1]+dbox*0.5,distro[0],width=dbox)
    plt.xlabel(xlabel)
    plt.ylabel("Counts")
    if save:
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=200)
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
        plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=200)
    plt.title(title)
    #plt.show()
    plt.close()
    return

def plotMultidistroFit(distarray,fitfun,popt,arraylabels=None,pixelsize=1,frametime=1,xlabel=r"dx [$\mu m$]",title="Step-Size-Distribution",save=True,path='.',bar=True):
    return

#=====================================

def linfun(x,D):
    return 4*D*x

def fitArray(msd,msdlength):
    #print len(msd)
    xdata = msd[0:min(msdlength,int(len(msd))),0]
    ydata = msd[0:min(msdlength,int(len(msd))),1]
    iniguess = [1]

    popt, pcov = curve_fit(linfun, xdata, ydata, iniguess)
    sys.stdout.flush()
    return popt,pcov


def findDiffConsts(msd,fitlength=0):
    diffC = []
    counter = 0
    for elem in msd:
        counter += 1
        if len(elem) == 0:
            counter -= 1
            continue
        if fitlength == 0:
            Dsaver,Dcov = fitArray(elem,int(len(elem)))
            diffC.append(np.array([len(elem),Dsaver[0],np.sqrt(np.diag(Dcov))[0]]))
        elif fitlength <= 1:
            Dsaver,Dcov = fitArray(elem,max(5,int(len(elem)*fitlength)))
            diffC.append(np.array([len(elem),Dsaver[0],np.sqrt(np.diag(Dcov))[0]]))
        else:
            Dsaver,Dcov = fitArray(elem,fitlength)
            diffC.append(np.array([len(elem),Dsaver[0],np.sqrt(np.diag(Dcov))[0]]))
    
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
    plt.savefig(path+'/EndToEndDistrib.png', format='png', dpi=200)
    #plt.show()
    plt.close()

    outarray = np.array([histo[1][1:]-(histo[1][1]-histo[1][0])/2,histo[0]]).transpose()
    fo = open(path+"/end2EndDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["displacement(pixel)","Counts"])
    print("End-To-End Displacement has been saved to folder.")
    return histo
    

def diffConstDistrib(tracks,track_ids,pixelsize,frametime,Dfactor,numberofbins=50,path='.'):

    print(("Starting Analysis of " + str(len(tracks)) + " single tracks."))
    print("....This will take a while...")
    print("........(creating a list of MSD from all tracks; this takes long...)")
    msdlist = list(map(msd,tracks))
    print("........(finding diffusion coefficient from all MSDs from list)")
    Dlist = findDiffConsts(msdlist,fitlength=0.2)
    Doutput = Dlist[:,1].mean()*Dfactor
    Doutput_err = Dlist[:,1].std()*Dfactor
    print(">>>> The average diffusion coefficient is: {:.05f}+-{:.05f} um^2/s".format(Doutput,Doutput_err))
    print("........(finding the lengths of the single tracks)")
    def lengthoftrack(tr):
        return tr[-1][0] - tr[0][0]
    lenList= np.array(list(map(lengthoftrack,tracks)))
    print((">>>> The average track length is: {:.05f}+-{:.05f} s".format(lenList.mean()*frametime,lenList.std()*frametime)))
    print(("Showing: Diffusion coefficient distribution of " + str(len(tracks)) + " tracks."))
    histo = np.histogram(Dlist[:,1],bins=numberofbins,range=(0,Dlist[:,1].mean()+Dlist[:,1].std()*5),density=False)
    bbs = np.array(list(histo[1])+[100000])
    histo = np.histogram(Dlist[:,1],bins=bbs,density=False)
    width = (histo[1][1]-histo[1][0])/2*Dfactor
    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111)
    ax.bar((histo[1][0:-1]+(histo[1][1]-histo[1][0])/2)*Dfactor,histo[0],width=width,label=r"{:.04f} +- {:.04f} $\mu$m$^2$/s".format(Dlist[:,1].mean()*Dfactor,Dlist[:,1].std()*Dfactor))
    #plt.axis([0,10,0,1])
    ax.set_title("Diffusion Coefficient Distribution")
    ax.set_ylabel("Counts")
    ax.set_xlabel(r"Diffusion Constants [$\mu m^2 s^{-1}$]")
    ax.legend()
    plt.savefig(path+'/DiffConstDistrib.png', format='png', dpi=200)
    #plt.show()
    plt.close('all')
    
    fo = open(path+"/Track_D_List.txt",'w')
    Doutlist = Dlist * np.array([frametime,Dfactor,Dfactor])
    printArrayToFile(Dlist,fo,head=["TrackLength(s)","D(um^2/s)","D_err(um^2/s)"])

    outarray = np.array([(histo[1][:-1]+(histo[1][1]-histo[1][0])/2)*Dfactor,histo[0]]).transpose()
    fo = open(path+"/diffConstDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["diffConst(um^2/s)","Counts"])
    
    print(("Showing: Length of tracks distribution for " + str(len(tracks)) + " tracks."))
    lenhist = np.histogram(lenList,range=(0,lenList.mean()+lenList.std()*5),bins=numberofbins,density=False)
    bbs = np.array(list(lenhist[1])+[100000])
    lenhist = np.histogram(lenList,bins=bbs,density=False)
    width = (lenhist[1][1]-lenhist[1][0])/2*frametime
    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111)
    ax.bar((lenhist[1][:-1]+(lenhist[1][1]-lenhist[1][0])/2)*frametime,lenhist[0],width=width)
    ax.set_title("Length Distribution of single tracks")
    ax.set_ylabel("Counts")
    ax.set_xlabel("Track length (s)")
    plt.savefig(path+'/lengthDistribution.png', format='png', dpi=200)
    #plt.show()
    plt.close('all')
    outarray = np.array([(lenhist[1][:-1]+(lenhist[1][1]-lenhist[1][0])/2)*frametime,lenhist[0]]).transpose()
    fo = open(path+"/lengthDistro.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(s)","Counts"])

    print(("Showing: Dependence of the diffusion coefficient on the track length of " + str(len(tracks)) + " individual tracks."))
    sys.stdout.flush()
    '''
    nubin = 30
    wbin = (lenhist[1][-2]-lenhist[1][0])/nubin
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
    '''
    plt.plot(Dlist[:,0]*frametime,Dlist[:,1]*Dfactor,'kx')
    plt.title("Dependence of the diffusion coefficient on the track length")
    plt.ylabel(r"Diffusion constant [$\mu m^2s^{-1}$]")
    plt.xlabel(r"Track length [s]")
    plt.savefig(path+'/trLengthDiffConstDependence.png', format='png', dpi=200)
    #plt.show()
    plt.close('all')
    outarray = np.array([Dlist[:,0],Dlist[:,1]]).transpose()
    fo = open(path+"/Length-Diffconst-Relation.txt",'w')
    printArrayToFile(outarray,fo,head=["track-length(frame)","meanDiffConst"])
    return Doutput, Doutput_err
#=======================================



#=== Combined Tracks analysis =================
def combineTracks(tracks,track_ids,path='.'):
    lastpart = np.zeros((len(tracks[0][0])))
    combtr = [np.array(lastpart)]
    combtracklist = [lastpart[:]]
    trlengths = []
    count = 0
    for tr in tracks:
        trlengths.append(tr[-1][0]-tr[0][0])
        lastpart = np.array(combtr[-1])
        for part in range(1,len(tr),1):
            outpart = []
            for i in range(len(tr[0])):
                if i < 3:
                    outpart.append(tr[part][i] - tr[0][i]+lastpart[i])
                else:
                    outpart.append(tr[part][i])
            combtr.append(np.array(outpart))
            outpart.append(track_ids[count])
            combtracklist.append(outpart[:])
        count += 1
    outfile = open(path+"/combinedTrack.txt",'w')
    head = ["Step","x","y","widthx","widthy","height","amplitude","sn","volume","track_id"]
    printArrayToFile(combtracklist,outfile,head)
    return np.array(combtr),np.mean(trlengths),np.std(trlengths)

def analyzeCombinedTrack(tracks,track_ids,pixelsize,frametime,Dfactor,lenMSD=500,fitrange=0.5,numberofbins=50,plotlen=30,path='.'):
    print(("Combining " + str(len(tracks)) + " tracks."))
    ct,averageL,stdL = combineTracks(tracks,track_ids,path=path)
    print("Average Track length is {:} +- {:}".format(averageL,stdL))
    plotTrack(ct.transpose(),path=path)
    print("Creating MSD for combined track.")
    lenMSD = max(int(averageL)-1,min(lenMSD,int(len(ct)*0.2)))
    fitlength = min(int(lenMSD),int(averageL*fitrange))
    print("Using {:} steps for MSD and fitting with {:} steps.".format(lenMSD,int(fitlength)))
    sys.stdout.flush()
    ct_msd = msd(ct,length=lenMSD)
    ct_diffconst = findDiffConsts([ct_msd],fitlength=fitlength)[0]
    print((">>>> Found diffusion coefficient: {:.05f}+-{:.05f} um^2/s".format(ct_diffconst[1]*Dfactor,ct_diffconst[2]*Dfactor)))
    of = open(path+"/MSD-combinedTrack.txt",'w')
    printArrayToFile(ct_msd,of,head=["Stpngize","MSD"])
    plotMSD(ct_msd,ct_diffconst[1],pxsize=pixelsize,frametime=frametime,xaxisrange=averageL+5*stdL,labelname=r"{:.04f}$\pm$ {:.04f} $\mu$m$^2$/s".format(ct_diffconst[1]*Dfactor,ct_diffconst[2]*Dfactor),path=path)
    print("Starting Distribution Analysis")
    distD, distDerr = distributionAnalysis(ct,pixelsize,frametime,Dfactor,plotlen,numberofbins=numberofbins,path=path)
    sys.stdout.flush()
    return ct_diffconst[1]*Dfactor, ct_diffconst[2]*Dfactor, distD, distDerr

def distributionAnalysis(track,pixelsize,frametime,Dfactor,plotlen,numberofbins=50,path='.'):
    dipllist = relativeStpng(track)
    print("....Saving Displacements to file.")
    outfile = open(path+"/combinedTrack-relativeXYDisplacements.txt",'w')
    printArrayToFile(dipllist,outfile,["Steppingtime","dx","dy"])

    def gaussfunc(x,sig,amp):
        return amp * np.exp(-(x)**2/(2*sig))

    def fitgauss(histo):
        try:
            popt,pcov = curve_fit(gaussfunc,histo[1][:-1]+(histo[1][1]-histo[1][0])/2,histo[0],bounds=[(0,0),(np.inf,np.inf)])
        except RuntimeError:
            print("Fit did not converge")
            popt = [1,1]
            pcov = [[1,1],[1,1]]
        return popt,pcov

    print("....Creating distribution of step sizes in x and y")
    dispdist = displacementDistro(dipllist)
    histograms = []
    fitparams = []
    maxval = np.max(np.absolute(dispdist[-1]))
    for elr2 in dispdist:
        histo = np.histogram(elr2,bins=numberofbins,range=(-maxval,maxval),density=False)
        popt,pcov = fitgauss(histo)
        histograms.append(list(histo))
        fitparams.append(list(popt))

    selecttimes = [0,4,8,16]
    fitparams = np.array(fitparams)
    factor = np.arange(1,len(fitparams)+1,1)*2*frametime
    Dfitlist = fitparams[:,0] / factor * pixelsize**2
    print(">>>> Average diffusion coefficent from fitting stepsize: {:.05f} +- {:.05f} um^2/s".format(Dfitlist.mean(),Dfitlist.std()))

    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111)
    colors = ['red','blue','orange','green']
    counter = 0
    title="Step-Size-Distribution"
    for elem in selecttimes:
        dbox = histograms[elem][1][1]-histograms[elem][1][0]
        xvals = histograms[elem][1][:-1]+dbox*0.5
        ax.plot(xvals*pixelsize,histograms[elem][0],'o',color=colors[counter],label=r"$\tau =$ {:.03f}s".format((int(elem)+1)*frametime))
        xvals = (np.arange(1000)/500 - 1)*maxval
        ax.plot(xvals*pixelsize,gaussfunc(xvals,fitparams[elem][0],fitparams[elem][1]),'-',color=colors[counter],label=r"$D =$ {:.04f}".format(Dfitlist[elem])+r"$\mu m^2s^{-1}$")
        counter += 1
    ax.set_xlabel(r"Displacement [$\mu m$]")
    ax.set_ylabel("Counts")
    ax.legend(loc='best')
    ax.set_title(title)
    plt.savefig(path+'/'+title+"-plot.png",format="png", dpi=200)
    plt.close('all')
    return Dfitlist.mean(), Dfitlist.std()
#===========================================


#====================================
#The big MAIN
#====================================
def doAnalysis(trackfile,pixelsize=0.100,frametime=0.1,minTrLength=10,fitrange=0.5,bCleanUpTracks=False,bSingleTrackMSDanalysis=True,bCombineTrack=True):
    #plotting parameters
    Dfactor = pixelsize*pixelsize/frametime

    lenMSD_ct = 100
    plotlen = 10 #gives the range of the distribution plots
    numberofbins = 70
    small = 20
    large = 100

    print()
    print()
    print("Reading Tracks Now")
    print("------------------")
    sys.stdout.flush()
    tracks, track_ids = readTracks(trackfile)

    #make file path for save files. making sure not to override existing analysis
    path = os.path.dirname(trackfile)
    trackfilename = trackfile[len(path)+1:]
    if len(trackfilename) > 35:
        spng = os.path.join(path,"SingleStateAnalysis_"+trackfilename[12:-4])
    else:
        spng = os.path.join(path,"SingleStateAnalysis")
    if not os.path.isdir(spng):
        os.mkdir(spng)
    else:
        spng = spng +"-"+strftime("%Y%m%d-%H%M%S")
        os.mkdir(spng)
    
    #Produce a cleaned up track file 
    if bCleanUpTracks:
        print()
        print("Cleaning Track File from NAN")
        print("----------------------------")
        sys.stdout.flush()
        cleanTracksFile(tracks,path+"/cleanedTracks.txt")
    

    #Implement Track restrictions. (E.g. minimum accepted track length)
    considered = []
    considered_ids = []
    for i in range(len(tracks)):
        if len(tracks[i]) >= minTrLength:
            considered.append(tracks[i])
            considered_ids.append(track_ids[i])
    if len(considered) == 0:
        print("Tracks are too short! Please adjust 'minTrackLen' to a lower value!")
        sys.stdout.flush()
        return
    elif len(considered) < 10:
        print("***** You have less then 10 eligible tracks available for analysis!! ******")
        print("***** The algorithm may fail.                                        ******")
        sys.stdout.flush()

    logfile = open(spng+'/analysis.log',"w")
    logfile.write("LogFile of the Analysis\n")
    logfile.write("=======================\n")
    logfile.write("Filename : " + trackfile + "\n")
    logfile.write("\n")
    logfile.write("Pixel Size : {:} um\n".format(pixelsize))
    logfile.write("Frame Interval: {:} s\n".format(frametime))
    logfile.write("Minimum Track length: {:} frames\n".format(minTrLength))
    logfile.write("Maximum frame lag for combined MSD: {:} frames\n".format(lenMSD_ct))
    logfile.write("\n")
    logfile.write("Number of considered tracks: {:}\n".format(len(considered)))
    trlens = []
    try:
        for tr in considered:
            if len(tr) == 0:
                continue
            trlens.append(tr[-1][0] - tr[0][0])
        trlens = np.array(trlens)
        logfile.write("Average Track length: {:}+-{:} frames\n".format(trlens.mean(),trlens.std()))
        logfile.write("\n")
    except RuntimeError:
        print("!!!!! Tracks are too short !!!!!!\nSee Log file for details on track lengths.")
        logfile.write("\nTracks are too short for analysis!!!\n")
        count = 0
        for tr in considered:
            logfile.write("Track {:} length: {:}".format(count,len(tr)))
            count += 1
        logfile.close()
        return
    except IndexError:
        print("!!!!! Index Error - There was a Problem with the Track file !!!!")
        logfile.write("\n!!!!! Index Error - There was a Problem with the Track file !!!!\n")
        logfile.close()
        return


    if (not bSingleTrackMSDanalysis) and (not bCombineTrack):
        ct,averageL,stdL = combineTracks(considered,considered_ids,path=path)
        return

    
    if bSingleTrackMSDanalysis:
        print()
        print()
        print("Starting Diffusion Constant Analysis for single tracks")
        print("------------------------------------------------------")
        diffC = diffConstDistrib(considered,considered_ids,pixelsize,frametime,Dfactor,numberofbins=numberofbins,path=spng)
        sys.stdout.flush()
        logfile.write("Individual Track Analysis\n")
        logfile.write("-------------------------\n")
        logfile.write("Average Diffusion Constant: {:}+-{:} um^2/s\n\n".format(diffC[0],diffC[1]))
    if bCombineTrack:
        print()
        print()
        print("Starting Combined Track Analysis")
        print("--------------------------------")
        Dmsd,Dmsd_err,Dstep,Dstep_err = analyzeCombinedTrack(considered,considered_ids,pixelsize,frametime,Dfactor,lenMSD=lenMSD_ct,fitrange=fitrange,numberofbins=numberofbins,plotlen=plotlen,path=spng)
        logfile.write("Combined Track Analysis\n")
        logfile.write("-----------------------\n")
        logfile.write("MSD diffusion constant: {:}+-{:} um^2/s\n".format(Dmsd,Dmsd_err))
        logfile.write("Step Distribution D: {:}+-{:} um^2/s\n".format(Dstep,Dstep_err))
    sys.stdout.flush()

    logfile.close()

    return
#=====================================



if __name__ == "__main__":
    trackfile = '/home/markus/Desktop/TestFiles/Analysis/foundTracks.txt'
    doAnalysis(trackfile,pixelsize=0.100,frametime=0.1,bCleanUpTracks=True,bSingleTrackMSDanalysis=True,bCombineTrack=True)

