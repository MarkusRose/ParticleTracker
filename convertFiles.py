'''======================================
===   Markus Rose                     ===
======================================'''

import numpy as np


#Read Trajectory from file
def readTrajectoryFromFile(filename):
    infile = open(filename,'r')
    infile.readline()
    infile.readline()
    line = infile.readline()

    track = []

    while line:
        [frame,x,y] = line.split()[:3]
        track.append([float(frame),float(x),float(y)])
        line = infile.readline()

    #print track
    return track


#Read Positions from file
def readPositionsFromFile(filename):
    infile = open(filename,'r')
    line = infile.readline()
    frame = line.split()[1]
    #print frame
    for i in xrange(3):
        infile.readline()
    line = infile.readline()

    pos = []

    while line:
        [x,y,wx,wy,h,a,sn,vo] = line.split()
        pos.append([int(frame),float(x),float(y),float(wx),
            float(wy),float(h),float(a),float(sn),float(vo)])
        line = infile.readline()
    
    infile.close()
    #print pos
    #print sorted(pos)
    return pos



def sortPositionFile(filename):
    pos = readPositionsFromFile(filename)
    posnew = sorted(pos, key=lambda x: x[1])
    
    outfile = open(filename,'r')
    line = ""
    outfile.readline()
    for i in xrange(3):
        line += outfile.readline()
    outfile.close()

    outfile = open(filename,'w')
    outfile.write("#- SORTED FRAME {:} -------- \n".format(posnew[0][0]))
    outfile.write(line)
    for a in posnew:
        yes = True
        for b in a:
            if yes:
                yes = False
                continue
            outfile.write(str(b) + ' ')
        outfile.write('\n')
    outfile.close()




def convertParticles(infile):
    i = 0
    boo = True
    particle = -4
    liste = []
    partnum = 0
    for line in infile:
        if line.strip():
            if boo:
                i += 1
                outfile = open("out{:0004d}.txt".format(i),'w')
                boo = False
            if not (particle < 0):
                if not line[0] == "#":
                    outfile.write(line)
                    partnum += 1
            elif particle == -1:
                outfile.write(line)
            else:
                outfile.write(line)
            particle += 1

        else:
            if not boo:
                if partnum >= 20:
                    liste.append(i)
                particle = -4
                partnum = 0
                outfile.close()
                sortPositionFile("out{:0004d}.txt".format(i))
            boo = True

    saveTN = open("SuggestedFrames.txt",'w')
    saveTN.write("Use the following tracks: \n" + str(liste))
    saveTN.close()


def convertTrajectories(infile):
    i = 0
    boo = True
    frame = -2
    liste = []
    partpos = 0
    for line in infile:
        if line.strip():
            if boo:
                i += 1
                outfile = open("out{:0004d}.txt".format(i),'w')
                boo = False
            if not (frame < 0):
                if not line[0] == "#":
                    outfile.write(str(frame)+ ' ' + line)
                    partpos += 1
            elif frame == -1:
                outfile.write("#frame " + line[1:])
            else:
                outfile.write(line)
            frame += 1

        else:
            if not boo:
                if partpos >= 50:
                    liste.append(i)
                frame = -2
                partpos = 0
                outfile.close()
            boo = True

    saveTN = open("SuggestedTrajectories.txt",'w')
    saveTN.write("Use the following tracks: \n" + str(liste))
    saveTN.close()



if __name__=="__main__":
    infile = open("foundTracks.txt",'r')
    convertTrajectories(infile)
    infile.close()
    infile = open("foundParticles.txt",'r')
    convertParticles(infile)
    infile.close()
