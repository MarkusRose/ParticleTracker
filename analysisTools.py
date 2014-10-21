'''==============================
=== Markus Rose               ===
=============================='''


import numpy as np
import cmath
import convertFiles


def calcMSD(track,fileident=""):
    delta = 1
    deltamax = track[len(track)-1][0] - track[0][0]
    print deltamax

    msd = []

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
                print("No data point found for delta = {:}".format(delta))
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
    tracks = convertFiles.readTrajectoryFromFile("trajectory2286.txt")
    calcMSD(tracks,"2286")
