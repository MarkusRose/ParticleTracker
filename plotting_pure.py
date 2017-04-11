import Detection.ctrack as ctrack
import AnalysisTools.driftCorrection as dc
import AnalysisTools.hiddenMarkov as hmm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection

import os
import sys
import numpy as np
import random


LII = 22
path = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li{:}/".format(LII)
SR = 20
Cel = ""
if LII == 22:
    if SR == 20:
        trackfile = "foundTracks-SR20_20170411-045006.txt"
elif LII == 24:
    if SR == 10:
        trackfile = "foundTracks-SR10_20170411-020113.txt"
    elif SR == 20:
        trackfile = "foundTracks-SR20_20170411-020152.txt"
    elif SR == 30:
        trackfile = "foundTracks-SR30_20170411-020242.txt"
elif LII == 27:
    if SR == 10:
        trackfile = "foundTracks-SR10_20170411-020450.txt"
    elif SR == 20:
        trackfile = "foundTracks-SR20_20170411-020530.txt"
    elif SR == 30:
        trackfile = "foundTracks-SR30_20170411-020623.txt"
elif LII == 30:
    if SR == 10:
        trackfile = "foundTracks-SR10_20170411-015207.txt"
    elif SR == 20:
        trackfile = "foundTracks-SR20_20170411-015803.txt"
    elif SR == 30:
        trackfile = "foundTracks-SR30_20170411-020335.txt"

small = 20
large = 100

pixel_size = 0.100 #um
timestep = 0.1 #s
Dfactor = pixel_size**2/timestep


if __name__=="__main__":

    #Theoretical upper and lower bounds
    Dmin = 0.01**2/(4*timestep)
    Dmax = (SR*pixel_size)**2/(4*timestep)

    #Conversion factor
    Dfactor = pixel_size*pixel_size/timestep

    #Change directory to input paths
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)


    #hmmdata = readInFile(hmmfile)
    tracks,z = ctrack.readTrajectoriesFromFile(trackfile,minTrackLen=1)
    indeces = []
    
    r2,leng,idfromtracks = hmm.squaredDisplacements(tracks)
    displ = []
    for tr in r2:
        displ += list(tr[0])
    displ = np.sqrt(displ)

    print("Maximum = {:} and Minimum = {:}".format(displ.max(),displ.min()))
    print("Plotting now")
    sys.stdout.flush()


    savepng = os.path.join(path,"Tracks-Cel{:}-SR{:}".format(Cel,SR))
    if not os.path.isdir(savepng):
        os.mkdir(savepng)
    os.chdir(savepng)


    userinput = 'n'
    if sys.platform == "win32": 
        print("Create plots of Tracks? [y,N]  ")
        sys.stdout.flush()

    userinput = raw_input("Create plots of Tracks? [y,N]  ") 
    num = 0
    plt.ioff()
    plt.show()

    if userinput == 'y':
        num = 2

        #tracks
        spng = os.path.join(savepng,"Tracks")
        if not os.path.isdir(spng):
            os.mkdir(spng)
        os.chdir(spng)
        counter = 0
        for track in tracks:
            counter += 1
            fig3 = plt.figure()
            ax3 = fig3.add_subplot(111, aspect='equal')
            tra = np.array(track.track[np.invert(np.isnan(track.track['x']))])
            if len(tra) == 0:
                j+=1
                print("Track of length 0???")
                continue
            z = tra['frame']*timestep#-tra[0]['frame']*timestep
            x = tra['x']*pixel_size
            y = tra['y']*pixel_size
            minx = x.min()
            miny = y.min()
            maxx = x.max()
            maxy = y.max()
            points = np.array([x,y]).T.reshape(-1,1,2)
            segments = np.concatenate([points[:-1],points[1:]],axis=1)
            lc = LineCollection(segments, cmap=plt.get_cmap('Spectral'),norm=plt.Normalize(0,z.max()))
            lc.set_array(z)
            lc.set_linewidth(2)
            ax3.add_collection(lc)
            plt.axis([minx-2*pixel_size,maxx+2*pixel_size,miny-2*pixel_size,maxy+2*pixel_size])
            axcb = fig3.colorbar(lc)
            axcb.set_label('time in $s$')
            ax3.set_xlabel(r'x in $\mu m$')
            ax3.set_ylabel(r'y in $\mu m$')
            plt.savefig("cd{:}.png".format(counter))
            #plt.draw()
            plt.close(fig3)
            print("Done {:}-{:}".format(0,counter))



    '''
    #Print All Tracks and Drift Tracks
    #================
    plt.ioff()
    plt.show()
    
    spng = os.path.join(path,"Tracks")
    if not os.path.isdir(spng):
        os.mkdir(spng)
    os.chdir(spng)

    #cellulases
    counter = 0
    for track in tracks:
        counter += 1
        fig3 = plt.figure()
        ax3 = fig3.add_subplot(111, aspect='equal')
        tra = np.array(track.track[np.invert(np.isnan(track.track['x']))])
        if len(tra) == 0:
            j+=1
            print("Track of length 0???")
            continue
        z = tra['frame']#-tra[0]['frame']*timestep
        x = tra['x']*pixel_size
        y = tra['y']*pixel_size
        minx = x.min()
        miny = y.min()
        maxx = x.max()
        maxy = y.max()
        points = np.array([x,y]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments, cmap=plt.get_cmap('Spectral'),norm=plt.Normalize(0,z.max()))
        lc.set_array(z)
        lc.set_linewidth(2)
        ax3.add_collection(lc)
        plt.axis([minx-2*pixel_size,maxx+2*pixel_size,miny-2*pixel_size,maxy+2*pixel_size])
        axcb = fig3.colorbar(lc)
        axcb.set_label('time in $s$')
        ax3.set_xlabel(r'x in $\mu m$')
        ax3.set_ylabel(r'y in $\mu m$')
        plt.savefig("temp{:}.png".format(counter))
        #plt.draw()
        plt.close(fig3)
        print("Done {:}-{:}".format(0,counter))
        '''
