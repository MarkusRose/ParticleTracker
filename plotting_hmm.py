from . import Detection.ctrack as ctrack
from . import AnalysisTools.driftCorrection as dc
from . import AnalysisTools.hiddenMarkov as hmm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection

import os
import sys
import numpy as np
import random


pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li24/"
#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li27/foundParticles.txt"
#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li30/foundParticles.txt"
SR = 10
Cel = ""
trackfile = "foundTracks-SR10_20170411-015207.txt"
trackfile = "foundTracks-SR20_20170411-015803.txt"
trackfile = "foundTracks-SR30_20170411-020335.txt"

small = 20
large = 100

pixel_size = 0.067 #um
timestep = 1 #s
Dfactor = pixel_size**2/timestep

if Cel == "5A":
    if SR == 5:
        boxup = np.array([0.06,0.094,1.01,1.7]) * Dfactor
        boxdown = np.array([0.05,0.09,0.22,0.4]) * Dfactor
        boxmid = np.array([0.12,0.13,0.1,0.3]) * Dfactor
    elif SR == 3:
        boxup = np.array([0.06,0.094,1.01,1.7]) * Dfactor
        boxdown = np.array([0.05,0.09,0.22,0.4]) * Dfactor
        boxmid = np.array([0.12,0.13,0.1,0.3]) * Dfactor
    elif SR == 2:
        boxup = np.array([0.00020,0.00035,0.0015,0.003])
        boxdown = np.array([0.00014,0.00025,0.0007,0.0012])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 1.5:
        boxup = np.array([0.00025,0.0004,0.0010,0.0022])
        boxdown = np.array([0.00014,0.00025,0.0005,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
elif Cel == "6B":
    if SR == 5:
        boxup = np.array([0.00010,0.00027,0.002,0.008])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 3:
        boxup = np.array([0.00010,0.00025,0.0015,0.004])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 2:
        boxup = np.array([0.00010,0.00025,0.0015,0.004])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 1.5:
        boxup = np.array([0.00013,0.0003,0.001,0.0025])
        boxdown = np.array([0.00005,0.00013,0.0005,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
elif Cel == "9A":
    if SR == 5:
        boxup = np.array([0.00007,0.0004,0.002,0.015])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 3:
        boxup = np.array([0.00007,0.0004,0.001,0.01])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 2:
        boxup = np.array([0.00007,0.0004,0.001,0.004])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])
    elif SR == 1.5:
        boxup = np.array([0.00007,0.0004,0.001,0.0025])
        boxdown = np.array([0.00005,0.00018,0.0003,0.001])
        boxmid = np.array([0.12,0.13,0.1,0.3])



class markovChain(object):
    
    struct_type = [('D1', np.double),
                   ('D2', np.double),
                   ('p12', np.double),
                   ('p21', np.double),
                   ('stdD1', np.double),
                   ('stdD2', np.double),
                   ('stdp12', np.double),
                   ('stdp21', np.double),
                   ('length',np.uint32)]
                    
    
    def __init__(self, num_elements):
        self.hmm = np.empty(num_elements, 
                              dtype=self.struct_type)
        self.id = np.empty(num_elements,dtype=(np.str_,16))
        
        for name in self.hmm.dtype.names:
            self.hmm[name].fill(0)
        self.id.fill('00000000')

    def readData(self,hmmlist):
        for i in range(len(hmmlist)):
            for j in range(len(hmmlist[i])):
                if j ==9:
                    self.id[i] = hmmlist[i][j]
                else:
                    self.hmm[i][self.hmm.dtype.names[j]] = hmmlist[i][j]
        return
        

def readInFile(filename):

    infile = open(filename,'r')

    allhmm = []
    for line in infile:
        td = []
        if line[0] == "#":
            header = line[:]
            continue
        saver = line.split()
        for i in range(len(saver)):
            if i==9:
                td.append(saver[i])
            elif i == 8:
                td.append(int(saver[i]))
            elif i == 0:
                a = float(saver[0])
                b = float(saver[1])
                if a > b:
                    continue
                else:
                    td.append(a)
            elif i == 1:
                a = float(saver[0])
                b = float(saver[1])
                if a > b:
                    td.append(b)
                    td.append(a)
                else:
                    td.append(b)
            else:
                td.append(float(saver[i]))
        allhmm.append(list(td))
    infile.close()


    hmmdata = markovChain(len(allhmm))
    hmmdata.readData(allhmm)

    return hmmdata
                
    

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
    dctracks,z = ctrack.readTrajectoriesFromFile(dcfile,minTrackLen=1)
    hmmdata = readInFile(hmm_file)
    indeces = []
    
    for box in [boxup,boxdown]:
        indeces.append(np.where(np.logical_and(hmmdata.hmm['length'] > large,
            np.logical_and(np.logical_and(hmmdata.hmm['D1'] > box[0]/Dfactor, hmmdata.hmm['D1'] < box[1]/Dfactor),
                np.logical_and(hmmdata.hmm['D2'] > box[2]/Dfactor, hmmdata.hmm['D2'] < box[3]/Dfactor)))))


    smallhmm = np.logical_and(hmmdata.hmm['length'] <= small,hmmdata.hmm['length'] > 1)
    mediumhmm = np.logical_and(hmmdata.hmm['length'] <= large,hmmdata.hmm['length'] > small)
    largehmm = hmmdata.hmm['length'] > large

    r2,leng,idfromtracks = hmm.squaredDisplacements(tracks)
    displ = []
    for tr in r2:
        displ += list(tr[0])
    displ = np.sqrt(displ)

    r2,leng,idfromtracks = hmm.squaredDisplacements(dctracks)
    driftdispl = []
    for tr in r2:
        driftdispl += list(tr[0])
    driftdispl = np.sqrt(displ)

    print(("Maximum = {:} and Minimum = {:}".format(displ.max(),displ.min())))
    print("Plotting now")
    sys.stdout.flush()


    savepng = os.path.join(path,"Tracks-Cel{:}-SR{:}".format(Cel,SR))
    if not os.path.isdir(savepng):
        os.mkdir(savepng)
    os.chdir(savepng)

    ofile = open("hmmStatistics-Cel{:}-SR{:}.txt".format(Cel,SR),'w')

    ofile.write("Statistics for Cel{:} with a search Radius of {:}\n".format(Cel,SR))
    ofile.write("=================================================\n\n")
    ofile.write("Mean D1 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm['D1']*Dfactor),np.std(hmmdata.hmm['D1']*Dfactor)))
    ofile.write("Mean D2 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm['D2']*Dfactor),np.std(hmmdata.hmm['D2']*Dfactor)))
    ofile.write("Mean p12 = {:} +- {:} \n".format(np.mean(hmmdata.hmm['p12']),np.std(hmmdata.hmm['p12'])))
    ofile.write("Mean p21 = {:} +- {:} \n\n".format(np.mean(hmmdata.hmm['p21']),np.std(hmmdata.hmm['p21'])))

    ofile.write("Short tracks with length <= {:} steps\n".format(small))
    ofile.write("-------------------------------------\n")
    ofile.write("Mean D1 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[smallhmm]['D1']*Dfactor),np.std(hmmdata.hmm[smallhmm]['D1']*Dfactor)))
    ofile.write("Mean D2 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[smallhmm]['D2']*Dfactor),np.std(hmmdata.hmm[smallhmm]['D2']*Dfactor)))
    ofile.write("Mean p12 = {:} +- {:} \n".format(np.mean(hmmdata.hmm[smallhmm]['p12']),np.std(hmmdata.hmm[smallhmm]['p12'])))
    ofile.write("Mean p21 = {:} +- {:} \n\n".format(np.mean(hmmdata.hmm[smallhmm]['p21']),np.std(hmmdata.hmm[smallhmm]['p21'])))

    ofile.write("Medium tracks with {:} < length <= {:} steps\n".format(small,large))
    ofile.write("--------------------------------------------\n")
    ofile.write("Mean D1 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[mediumhmm]['D1']*Dfactor),np.std(hmmdata.hmm[mediumhmm]['D1']*Dfactor)))
    ofile.write("Mean D2 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[mediumhmm]['D2']*Dfactor),np.std(hmmdata.hmm[mediumhmm]['D2']*Dfactor)))
    ofile.write("Mean p12 = {:} +- {:} \n".format(np.mean(hmmdata.hmm[mediumhmm]['p12']),np.std(hmmdata.hmm[mediumhmm]['p12'])))
    ofile.write("Mean p21 = {:} +- {:} \n\n".format(np.mean(hmmdata.hmm[mediumhmm]['p21']),np.std(hmmdata.hmm[mediumhmm]['p21'])))

    ofile.write("Long tracks with length > {:} steps\n".format(large))
    ofile.write("------------------------------------\n")
    ofile.write("Mean D1 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[largehmm]['D1']*Dfactor),np.std(hmmdata.hmm[largehmm]['D1']*Dfactor)))
    ofile.write("Mean D2 = {:} +- {:} um^2 s^-1\n".format(np.mean(hmmdata.hmm[largehmm]['D2']*Dfactor),np.std(hmmdata.hmm[largehmm]['D2']*Dfactor)))
    ofile.write("Mean p12 = {:} +- {:} \n".format(np.mean(hmmdata.hmm[largehmm]['p12']),np.std(hmmdata.hmm[largehmm]['p12'])))
    ofile.write("Mean p21 = {:} +- {:} \n\n".format(np.mean(hmmdata.hmm[largehmm]['p21']),np.std(hmmdata.hmm[largehmm]['p21'])))

    ofile.close()

    averages = np.zeros((8,4))
    averages[0,0] = np.mean(hmmdata.hmm['D1']*Dfactor)
    averages[1,0] = np.mean(hmmdata.hmm['D2']*Dfactor)
    averages[2,0] = np.mean(hmmdata.hmm['p12'])
    averages[3,0] = np.mean(hmmdata.hmm['p21'])
    averages[4,0] = np.std(hmmdata.hmm['D1']*Dfactor)
    averages[5,0] = np.std(hmmdata.hmm['D2']*Dfactor)
    averages[6,0] = np.std(hmmdata.hmm['p12'])
    averages[7,0] = np.std(hmmdata.hmm['p21'])
    averages[0,1] = np.mean(hmmdata.hmm[smallhmm]['D1']*Dfactor)
    averages[1,1] = np.mean(hmmdata.hmm[smallhmm]['D2']*Dfactor)
    averages[2,1] = np.mean(hmmdata.hmm[smallhmm]['p12'])
    averages[3,1] = np.mean(hmmdata.hmm[smallhmm]['p21'])
    averages[4,1] = np.std(hmmdata.hmm[smallhmm]['D1']*Dfactor)
    averages[5,1] = np.std(hmmdata.hmm[smallhmm]['D2']*Dfactor)
    averages[6,1] = np.std(hmmdata.hmm[smallhmm]['p12'])
    averages[7,1] = np.std(hmmdata.hmm[smallhmm]['p21'])
    averages[0,2] = np.mean(hmmdata.hmm[mediumhmm]['D1']*Dfactor)
    averages[1,2] = np.mean(hmmdata.hmm[mediumhmm]['D2']*Dfactor)
    averages[2,2] = np.mean(hmmdata.hmm[mediumhmm]['p12'])
    averages[3,2] = np.mean(hmmdata.hmm[mediumhmm]['p21'])
    averages[4,2] = np.std(hmmdata.hmm[mediumhmm]['D1']*Dfactor)
    averages[5,2] = np.std(hmmdata.hmm[mediumhmm]['D2']*Dfactor)
    averages[6,2] = np.std(hmmdata.hmm[mediumhmm]['p12'])
    averages[7,2] = np.std(hmmdata.hmm[mediumhmm]['p21'])
    averages[0,3] = np.mean(hmmdata.hmm[largehmm]['D1']*Dfactor)
    averages[1,3] = np.mean(hmmdata.hmm[largehmm]['D2']*Dfactor)
    averages[2,3] = np.mean(hmmdata.hmm[largehmm]['p12'])
    averages[3,3] = np.mean(hmmdata.hmm[largehmm]['p21'])
    averages[4,3] = np.std(hmmdata.hmm[largehmm]['D1']*Dfactor)  
    averages[5,3] = np.std(hmmdata.hmm[largehmm]['D2']*Dfactor)
    averages[6,3] = np.std(hmmdata.hmm[largehmm]['p12'])
    averages[7,3] = np.std(hmmdata.hmm[largehmm]['p21'])

    #Plot dependence of D1, D2, p12,p21 on track length category
    fig4,axs = plt.subplots(nrows=2,ncols=2, sharex=True)
    labels = ['all',r'$\Delta t<{:}s$'.format(small*timestep),r'${:}s < \Delta t < {:}s$'.format(small*timestep,large*timestep),r'$\Delta t>{:}s$'.format(large*timestep)]
    ax = axs[0,0]
    ax.errorbar(np.arange(4),averages[0],yerr=averages[0+4],fmt='o-',color='r')
    ax.set_ylabel(r"D1 in $\mu m^2s^{-1}$")
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels,rotation=40)
    ax2= axs[0,1]
    ax2.errorbar(np.arange(4),averages[1],yerr=averages[1+4],fmt='o-',color='r')
    ax2.set_ylabel(r"D2 in $\mu m^2s^{-1}$")
    ax2.set_xticks(np.arange(4))
    ax2.set_xticklabels(labels,rotation=40)
    ax3= axs[1,0]
    ax3.errorbar(np.arange(4),averages[2],yerr=averages[2+4],fmt='o-',color='r')
    ax3.set_ylabel(r"p12")
    ax3.set_xticks(np.arange(4))
    ax3.set_xticklabels(labels,rotation=40)
    ax4 = axs[1,1]
    ax4.errorbar(np.arange(4),averages[3],yerr=averages[3+4],fmt='o-',color='r')
    ax4.set_ylabel(r"p21")
    ax4.set_xticks(np.arange(4))
    ax4.set_xticklabels(labels,rotation=40)
    plt.xlabel("Length Category")
    plt.tight_layout()
    plt.savefig("valueDependenceCel{:}SR{:}.png".format(Cel,SR))
    plt.draw()

    #Plot stepsize distribution
    fig8 = plt.figure()
    ax8 = fig8.add_subplot(111)
    ax8.hist(displ,50)
    ax8.set_xlabel("step length (px)")
    ax8.set_ylabel("count")
    ax8.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.savefig("stepsCel{:}SR{:}.png".format(Cel,SR))
    plt.draw()
    
    #Plot stepsize distribution
    fig8 = plt.figure()
    ax8 = fig8.add_subplot(111)
    ax8.hist(driftdispl,50)
    ax8.set_xlabel("step length (px)")
    ax8.set_ylabel("count")
    ax8.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.savefig("driftstepsCel{:}SR{:}.png".format(Cel,SR))
    plt.draw()
    

    #Plot track length distribution
    fig6 = plt.figure()
    ax6 = fig6.add_subplot(111)
    ax6.hist(hmmdata.hmm[largehmm]['length']*timestep,50)
    ax6.set_xlabel("track time (s)")
    ax6.set_ylabel("count")
    plt.savefig("lengthsCel{:}SR{:}.png".format(Cel,SR))
    plt.draw()

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, aspect='equal')
    ax2.loglog(hmmdata.hmm[smallhmm]['D1']*Dfactor,hmmdata.hmm[smallhmm]['D2']*Dfactor,'y.',zorder=1,label=r"$\Delta t<${:}".format(small*timestep))
    ax2.loglog(hmmdata.hmm[mediumhmm]['D1']*Dfactor,hmmdata.hmm[mediumhmm]['D2']*Dfactor,'b.',zorder=2,label=r"{:}$<\Delta t<${:}".format(small*timestep,large*timestep))
    ax2.loglog(hmmdata.hmm[largehmm]['D1']*Dfactor,hmmdata.hmm[largehmm]['D2']*Dfactor,'r^',zorder=3,label=r"$\Delta t>${:}".format(large*timestep))
    for box in [boxup,boxdown]:
        ax2.add_patch(
                patches.Rectangle(
                    (box[0], box[2]),
                    box[1]-box[0],
                    box[3]-box[2],
                    fill=False,      # remove background
                    linewidth=2,
                    zorder=10
                    )
                )
    ax2.add_patch(
            patches.Rectangle(
                (Dmin, Dmin),
                Dmax-Dmin,
                Dmax-Dmin,
                fill=False,      # remove background
                linewidth=2,
                zorder=10,
                color='0.75'
                )
            )
    ax2.legend()
    plt.xlabel(r"D1 in $\mu m^2 s^{-1}$")
    plt.ylabel(r"D2 in $\mu m^2 s^{-1}$")
    plt.title("Cel{0:}-SR{1:}".format(Cel,SR))
    plt.savefig("hmm-Cel{0:}-SR{1:}.png".format(Cel,SR))
    plt.draw()

    fig = plt.figure()
    for index in indeces[0][0]:
        tra = np.array(tracks[index].track[np.invert(np.isnan(tracks[index].track['x']))])
        if len(tra) == 0:
            print("We have a problem here: long track length short")
            continue
        z = tra['frame']-tra[0]['frame']
        x = tra['x']
        y = tra['y']
        points = np.array([x,y]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments, cmap=plt.get_cmap('Spectral'),norm=plt.Normalize(0,400))
        lc.set_array(z)
        lc.set_linewidth(1)
        plt.gca().add_collection(lc)
    plt.axis([0,400,0,400])
    axcb = fig.colorbar(lc)
    axcb.set_label('frame')
    plt.show(block=True)
    

    userinput = 'n'
    if sys.platform == "win32": 
        print("Create plots of Tracks? [y,N]  ")
        sys.stdout.flush()

    userinput = input("Create plots of Tracks? [y,N]  ") 
    num = 0
    plt.ioff()
    plt.show()

    if userinput == 'y':
        num = 2

        for i in range(len(indeces)):
            spng = os.path.join(savepng,"Box-{:}".format(i))
            if not os.path.isdir(spng):
                os.mkdir(spng)
            os.chdir(spng)
            difference = 0
            j = 0
            while j < len(indeces[i][0]):
                if hmmdata.id[indeces[i][0][j]] != tracks[indeces[i][0][j]+difference].id:
                    difference += 1
                    print(("Problem! {:}".format(hmmdata.id[indeces[i][0][j]])))
                    continue
                fig3 = plt.figure()
                ax3 = fig3.add_subplot(111, aspect='equal')
                tra = np.array(tracks[indeces[i][0][j]+difference].track[np.invert(np.isnan(tracks[indeces[i][0][j]+difference].track['x']))])
                if len(tra) == 0:
                    j+=1
                    print("Track of length 0???")
                    continue
                z = tra['frame']-tra[0]['frame']*timestep
                x = tra['x']*pixel_size
                y = tra['y']*pixel_size
                minx = x.min()
                miny = y.min()
                maxx = x.max()
                maxy = y.max()
                points = np.array([x,y]).T.reshape(-1,1,2)
                segments = np.concatenate([points[:-1],points[1:]],axis=1)
                lc = LineCollection(segments, cmap=plt.get_cmap('Spectral'),norm=plt.Normalize(0,len(tracks[indeces[i][0][j]+difference].track['frame'])))#z.max()))
                lc.set_array(z)
                lc.set_linewidth(2)
                ax3.add_collection(lc)
                plt.axis([minx-2*pixel_size,maxx+2*pixel_size,miny-2*pixel_size,maxy+2*pixel_size])
                axcb = fig3.colorbar(lc)
                axcb.set_label('time in $s$')
                ax3.set_xlabel(r'x in $\mu m$')
                ax3.set_ylabel(r'y in $\mu m$')
                plt.savefig("temp{:}.png".format(j))
                #plt.draw()
                plt.close(fig3)
                print(("Done {:}-{:}".format(i,j)))
                j += 1

        #drift
        spng = os.path.join(savepng,"Drift")
        if not os.path.isdir(spng):
            os.mkdir(spng)
        os.chdir(spng)
        counter = 0
        for track in dctracks:
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
            plt.savefig("cd{:}.png".format(counter))
            #plt.draw()
            plt.close(fig3)
            print(("Done {:}-{:}".format(0,counter)))



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
