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



path = "/media/markus/DataPartition/Cellulases-Analysis/"
SR = 5
Cel = "5A"
trackfile = "foundTracks-Cel{0:}-SR{1:}.txt".format(Cel,SR)
hmmfile = "hmmAveragedData-Cel{0:}-SR{1:}.txt".format(Cel,SR)

minlength = 100


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
        for i in xrange(len(hmmlist)):
            for j in xrange(len(hmmlist[i])):
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
        for i in xrange(len(saver)):
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

    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)

    hmmdata = readInFile(hmmfile)
    tracks,z = ctrack.readTrajectoriesFromFile(trackfile,minTrackLen=1)
    print tracks[0].id

    print len(hmmdata.hmm)

    print len(hmmdata.hmm[hmmdata.hmm['length'] > 100]['D1'])

    box = (0.12,0.13,0.1,0.3)
    indeces = np.where(np.logical_and(hmmdata.hmm['length'] > 10,
        np.logical_and(np.logical_and(hmmdata.hmm['D1'] > box[0], hmmdata.hmm['D1'] < box[1]),
            np.logical_and(hmmdata.hmm['D2'] > box[2], hmmdata.hmm['D2'] < box[3]))))


    print hmmdata.hmm[indeces[0][0]]
    print hmmdata.id[indeces[0][0]]

    print tracks[indeces[0][0]].id



    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, aspect='equal')
    ax2.loglog(hmmdata.hmm[hmmdata.hmm['length'] > 1]['D1'],hmmdata.hmm[hmmdata.hmm['length'] > 1]['D2'],'y+',zorder=1)
    ax2.loglog(hmmdata.hmm[hmmdata.hmm['length'] > 10]['D1'],hmmdata.hmm[hmmdata.hmm['length'] > 10]['D2'],'b.',zorder=2)
    ax2.loglog(hmmdata.hmm[hmmdata.hmm['length'] > 100]['D1'],hmmdata.hmm[hmmdata.hmm['length'] > 100]['D2'],'ro',zorder=3)
    ax2.add_patch(
            patches.Rectangle(
                (box[0], box[2]),
                box[1]-box[0],
                box[3]-box[2],
                fill=False,      # remove background
                linewidth=3,
                zorder=10
                )
            )
    plt.show()
    

    fig = plt.figure()
    for i in xrange(len(indeces[0])):
        tra = np.array(tracks[indeces[0][i]].track[np.invert(np.isnan(tracks[indeces[0][i]].track['x']))])
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
    plt.show()
