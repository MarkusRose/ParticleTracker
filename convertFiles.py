'''======================================
===   Markus Rose                     ===
======================================'''

import numpy as np
import detectParticles
import analysisTools
import pysm.new_cython


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

def readDetectedParticles(filename):
    infile = open(filename,'r')
    particle_data=[]
    line = infile.readline()
    while line:
        particle_oneframe=[]
        line = infile.readline()
        frame = line.split()[1]
        line = infile.readline()
        partnum = float(line.split()[1])
        line = infile.readline()
        cutoff = float(line.split()[1])
        line = infile.readline()
        line = infile.readline()
        while line and line.strip():
            a = line.split()
            b = []
            for k in a:
                b.append(float(k))
            p = pysm.new_cython.TempParticle()        
            p.frame = frame
            p.x,p.y,p.width_x,p.width_y,p.height,p.amplitude,p.sn,p.volume = b
            particle_oneframe.append(p)
            line = infile.readline()
        if len(particle_oneframe) != partnum:
            print "We have a problem"
            break
        particle_data.append([particle_oneframe,cutoff])

    infile.close()

#    detectParticles.writeDetectedParticles(particle_data)
    pd = []
    for fr in particle_data:
        pd.append(fr[0])
#    print pd
    return pd


def sortPositionFile(filename):
    pos = readPositionsFromFile(filename)
    posnew = sorted(pos, key=lambda x: x[1])
    #print pos
    #print posnew
    
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
                outfile = open("frame{:0004d}.txt".format(i),'w')
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
                sortPositionFile("frame{:0004d}.txt".format(i))
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
                outfile = open("trajectory{:0004d}.txt".format(i),'w')
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
                if partpos >= 20:
                    liste.append(i)
                frame = -2
                partpos = 0
                outfile.close()
            boo = True

    saveTN = open("SuggestedTrajectories.txt",'w')
    saveTN.write("Use the following tracks: \n" + str(liste))
    saveTN.close()

    for t in liste:
        tracks = readTrajectoryFromFile("trajectory{:0004d}.txt".format(t))
        analysisTools.calcMSD(tracks,"{:0004d}".format(t))

def convImageJTrack(filename):
    infile = open(filename,'r')
    infile.readline()
    traject = []

    for line in infile:
        x = int(float(line.split()[4])/0.16 - 0.5)
        y = int(float(line.split()[5])/0.16 - 0.5)
        t = int(float(line.split()[6])/0.16)
        traject.append([t,x,y])

    return traject





if __name__=="__main__":
    '''
    infile = open("foundTracks.txt",'r')
    convertTrajectories(infile)
    infile.close()
    infile = open("foundParticles.txt",'r')
    convertParticles(infile)
    infile.close()
    '''
    #readDetectedParticles("foundParticles.txt")
    print convImageJTrack("/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/VisTrack01.xls")
