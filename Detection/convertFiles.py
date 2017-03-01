'''======================================
===   Markus Rose                     ===
======================================'''

import numpy as np
import detectParticles
import analysisTools
import pysm.new_cython
import markPosition


#Read Trajectory from file
def readTrajectoryFromFile(filename):
    infile = open(filename,'r')
    infile.readline()
    infile.readline()
    line = infile.readline()

    track = []

    while line:
        if (not line.strip()) or line[0] == '#':
            line = infile.readline()
            continue
        [frame,x,y] = line.split()[:3]
        track.append({"frame":float(frame),"x":float(x),"y":float(y)})
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

def writeParticleFile(positions,filename="foundParticles.txt"):
    outfile = open(filename,'w')
    for i in xrange(len(positions)):
        detectParticles.writeDetectedParticles([positions[i],0.0],i+1,outfile)
    outfile.close()
    return



def readDetectedParticles(filename):
    infile = open(filename,'r')
    particle_data=[]

    emptycounter = 0
    hashcounter = 0
    frame = 0

    oneframe = []
    
    for line in infile:
        if len(line.split()) == 0:
            emptycounter += 1
            if len(oneframe) != 0:
                if len(oneframe) != partnum:
                    print "Number of particles and Frame content don't match!"
                    raise
                particle_data.append(list(oneframe))
                oneframe = []
        elif line[0] == '#':
            hashcounter += 1
            if hashcounter % 4 == 1:
                frame  = int(line.split()[1])
            elif hashcounter % 4 == 2:
                partnum = float(line.split()[1])
            elif hashcounter % 4 == 3:
                cutoff = float(line.split()[1])
            elif hashcounter % 4 == 0:
                oneframe = []
            else:
                continue
        else:
            b = []
            for k in line.split():
                b.append(float(k))
            p = pysm.new_cython.TempParticle()        
            p.frame = frame
            p.x,p.y,p.width_x,p.width_y,p.height,p.amplitude,p.sn,p.volume = b
            oneframe.append(p)
    if len(oneframe) > 0:
        particle_data.append(list(oneframe))
        if len(oneframe) != partnum:
            print "Number of particles and Frame content don't match!"
            raise
        del oneframe

#    print("Empty lines: {:}".format(emptycounter))
#    print("Hashtag lines: {:}".format(hashcounter))
    
    return particle_data

    '''
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
    return pd
    '''


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

def convertTrajectories(infile,minTrackLen):
    print("Hello There")
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
            print "else"
            if not boo:
                if partpos >= minTrackLen:
                    liste.append(i)
                print frame
                frame = -2
                partpos = 0
                outfile.close()
                boo = True

    saveTN = open("SuggestedTrajectories.txt",'w')
    saveTN.write("Use the following tracks: \n" + str(liste))
    saveTN.close()

    for t in liste:
        tracks = readTrajectoryFromFile("trajectory{:0004d}.txt".format(t))
        m = markPosition.connectPositions((512,512),tracks)
        markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"tr{:0004d}.tif".format(t))
        analysisTools.calcMSD(tracks,"{:0004d}".format(t))

    return


def convImageJTrack(filename):
    infile = open(filename,'r')
    infile.readline()
    traject = []

    for line in infile:
        if not line.strip():
            continue
        x = int(float(line.split()[2])/0.16 - 0.5)
        y = int(float(line.split()[1])/0.16 - 0.5)
        t = int(float(line.split()[3]))
        traject.append([t,x,y])

    return sorted(traject)



def giveLocalMaxValues(track,length):
    local_max = []
    counter = 0
    for i in track:
        counter += 1
        while i[0] > counter:
            counter += 1 
            local_max.append([[0],[0]])
        if i[0] < counter:
            counter -=1
            local_max[-1][0].append(i[1])
            local_max[-1][1].append(i[2])
        else:
            local_max.append([[i[1]],[i[2]]])

    while counter < length:
        counter += 1
        local_max.append([[0],[0]])

    return local_max
        

if __name__=="__main__":
    loc = giveLocalMaxValues(convImageJTrack("testterer.txt"),7)
    print loc
    
