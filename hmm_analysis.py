import numpy as np
import sys

import AnalysisTools.driftCorrection as dc
import Detection.ctrack as ctrack



if __name__=="__main__":

    '''
    driftfile = "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR2_20170209-020552.txt"
    trackfile = "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt"
    '''
    driftfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"
    trackfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"

    drifttracks,driftlist = ctrack.readTrajectoriesFromFile(driftfile)
    part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)

    pt = dc.driftCorrection(drifttracks,part_tracks)




def testerFunction1(folder,runs):
    allTracks2 = readSimTrack(folder+'/foundTracks.txt')
    anaTr = []
    for t in allTracks2:
        for p in t:
            anaTr.append(np.array(p))
    anaTr = np.array(anaTr)
    '''
    sha = allTracks2.shape
    allTracks = allTracks2.reshape(sha[0]*sha[1],sha[2])
    '''
    Thetas = []
    for i in xrange(max(runs,anaTr[-1:-1])):
        theta, L, nurun = doMetropolisOrig(anaTr,folder,i)
        theta = np.array(theta)
        theta1 = 10**theta[:,0]
        theta2 = 10**theta[:,1]
        p12 = theta[:,2]
        p21 = theta[:,3]
        
        fig1, (ax1,ax2) = plt.subplots(2,1)
        ax1.plot(theta1,'gx')
        ax1.plot(theta2,'rx')
        
        ax2.plot(p12,'gx')
        ax2.plot(p21,'rx')
        plt.show()
        
        thetaMean = [np.mean(theta1[1000:]),np.mean(theta2[1000:]),np.mean(p12[1000:]), np.mean(p21[1000:])]
        thetaSTD = [np.std(theta1[1000:]),np.std(theta2[1000:]),np.std(p12[1000:]), np.std(p21[1000:])]
        Thetas.append([np.array(thetaMean),np.array(thetaSTD)])
        print thetaMean
        
        statemap = segmentstate(thetaMean, anaTr, i)
        trackout = open("trackstates{:04d}.txt".format(0),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
    outthetaf = open("AveragedData.txt",'w')
    outtheta.write("#  D1 D2 p12 p21 stds: D1 D2 p12 p21\n")
    for line in Thetas:
        for ones in line:
            for elem in ones:
                outtheta.write("{:} ".format(elem))
        outtheta.write("\n")
    outtheta.close()
    
    return
    
    

def main(folder,reps):
    allTracks2 = readTracks(folder+'/foundTracks.txt')
    anaTr = []
    for t in allTracks2:
        for p in t:
            anaTr.append(np.array(p))
    anaTr = np.array(anaTr)
    '''
    sha = allTracks2.shape
    allTracks = allTracks2.reshape(sha[0]*sha[1],sha[2])
    '''

    numparts = anaTr[-1][-1]
    outtheta = []
    runs = []
    counter = 1
    print numparts
    rawout = open("rawDataout.txt", 'w')
    rawout.write("# Analysis of Cel5A \n# D1  D2   p12  p21  nuruns\n")
    sumout = open("avHmmData.txt",'w')
    sumout.write("# Analysis of Cel5A \n# D1  D2   p12  p21  nuruns stds....\n")

    while counter-1 < numparts:
        rawout.write("# Track {:}\n".format(counter))
        avTheta = []
        avNuruns = []
        for k in xrange(reps):
            print "    Run {:},{:}".format(counter,k+1)
            theta,L,nuruns = doMetropolis3(anaTr,folder,counter)
            if theta[-1][0] > theta[-1][1]:
                results = np.array([theta[-1][1],theta[-1][0],theta[-1][3],theta[-1][2]])
            else:
                results = np.array(theta[-1])
            avTheta.append(np.array(results))
            avNuruns.append(nuruns)
            rawout.write("{:} {:} {:} {:} {:}\n".format(results[0], results[1], results[2], results[3], nuruns))
        thetaMean = np.mean(avTheta,axis=0)
        thetaStd = np.std(avTheta,axis=0)
        outtheta.append([np.array(thetaMean),np.array(thetaStd)])
        runs.append([np.mean(avNuruns),np.std(avNuruns)])
        sumout.write("{:} {:} {:} {:} {:} {:} {:} {:} {:} {:}\n"
                     .format(thetaMean[0], thetaMean[1], thetaMean[2], thetaMean[3], np.mean(avNuruns),thetaStd[0],thetaStd[1],thetaStd[2],thetaStd[3],np.std(avNuruns)))
        rawout.write("\n\n")
        statemap = segmentstate(thetaMean, anaTr, counter)
        trackout = open("trackstates{:04d}.txt".format(counter),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
        counter += 1
    return outtheta, runs
        

