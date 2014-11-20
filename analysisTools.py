'''==============================
=== Markus Rose               ===
=============================='''


import numpy as np
import cmath
import convertFiles
import ctrack

def sortOutTrack(track):
    outtrack = []
    for i in track:
        if np.isnan(i['x']):
            continue
        else:
            outtrack.append([i['frame'],i['x'],i['y']])
    return outtrack

def addTwoTracks(trackA,trackB):
    out = []
    for i in trackA:
        out.append([i[0],i[1],i[2]])
    relf = trackB[0][0]
    relx = trackB[0][1]
    rely = trackB[0][2]
    check1 = True
    for j in trackB:
        if check1:
            check1 = False
            continue
        out.append([j[0]-relf+i[0],j[1]-relx+i[1],j[2]-rely+i[2]])

    return out
        

def appendTrajectories(tracks,liste):
    outtrack = []
    c1 = True
    for i in liste:
        tA = sortOutTrack(tracks[i].track)
        if c1:
            c1 = False
            outtrack = list(tA)
            continue
        outtrack = addTwoTracks(outtrack,tA)
    print len(outtrack)
    print outtrack[-1][0]
    return outtrack


def calcMSD(track,fileident=""):
    delta = 1
    deltamax = track[len(track)-1][0] - track[0][0]
    print len(track)
    print deltamax

    msd = []
    if deltamax > 300:
        deltamax = 300

    while delta < deltamax:
        numofdata = 0
        sum = 0

        for j in xrange(len(track)-delta):
            notfound = False
            for i in xrange(j+1,j+delta+1,1):
                if (track[i][0] < delta + track[j][0]):
                    continue
                elif (track[i][0] > delta + track[j][0]):
                    notfound = True
                    break
                else:
                    numofdata+=1
                    break

            if notfound:
                #print("No data point found for delta = {:}".format(delta))
                continue
            dx = track[i][1]-track[j][1]
            dy = track[i][2]-track[j][2]
            sum += ( dx*dx + dy*dy )

        if numofdata != 0:
            print(str(delta)+' '+str(numofdata))
            sum /= numofdata
            msd.append([delta,sum])
        
        delta += 1

    print(msd)

    outfile = open("msd"+fileident+".txt",'w')

    for a in msd:
        outfile.write(str(a[0]) + ' ' + str(a[1]) + '\n')
    outfile.close()
    return


def calcSCF(track,fileident=""):
    #Parameters
    L = 2
    vels = []

    v=0
    for i in xrange(len(track)-1):
        dx = track[i+1][1]-track[i][1]
        dy = track[i+1][2]-track[i][2]
        v = cmath.sqrt(dx*dx+dy*dy)/(track[i+1][0]-track[i][0])
        vels.append(v)
    vels.append(v)
    if len(track) != len(vels):
        print "Velocities don't match track."
    
    return

    for j in xrange(L):
        k = j
        while k < (track[-1][0]-track[0][0]-L):
            v = 0
            for i in xrange(k,k+L,1):
                dx = track[i+1][1]-track[i][1]
                dy = track[i+1][2]-track[i][2]
                v += cmath.sqrt(dx*dx + dy*dy)/(track[i+1][0]-track[i][0])
            v /= L
            k += L


if __name__=="__main__":
    tracks = convertFiles.convImageJTrack("/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/VisTrack01.xls")
    calcMSD(tracks)
