import numpy as np
from PIL import Image

import Detection.ctrack
from . import detectParticles
from . import markPosition
import main
from . import convertFiles

# Determine image properties
size = 512
v = 10
omega = np.pi*2/100
R = 20
numframes = 1000
x, y = 10,size/2

def circleDrawer():
    frames = np.array(list(range(numframes)))
    xpos = R * np.cos(omega * frames)
    ypos = R * np.sin(omega * frames)
    return frames, xpos, ypos

def straightDrawer():
    frames = np.array(list(range(numframes)))
    xpos = v*frames
    ypos = 0*frames
    return frames, xpos, ypos

def calcer(frames,xpos,ypos):
    particle_data = []
    track = ctrack.ParticleTrack(id=1,num_elements=numframes)
    trajectories = []
    outf = open("circle.txt", 'w')
    outf.write("#frame, xpos, ypos \n")
    for i in range(len(frames)):
        particle = ctrack.makeParticle(frames[i],x+xpos[i],y+ypos[i],1,1,0,1)
        particle_data.append([particle])
        track.insert_particle(particle,particle.frame)
        detectParticles.writeDetectedParticles([[particle],0],frames[i],outf)
    trajectories.append(track)
    outf.close()
    ctrack.writeTrajectories(trajectories,filename="circletrack.txt")
    for i in range(len(trajectories)):
        m = markPosition.connectPositions((size,size),trajectories[i].track)
        markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"circle{:01d}.tif".format(i))
    print(len(trajectories))

    return particle_data

def main():
    convertFiles.readDetectedParticles("../foundParticles.txt")
    '''
    f,x,y = straightDrawer()
    particle_data = calcer(f,x,y)

    tr = main.makeTracks(particle_data)
    tr,liste = ctrack.readTrajectoriesFromFile("foundTracks.txt")
    for t in liste:
        print "doing track {:}".format(t)
        m = markPosition.connectPositions((512,512),tr[t-1].track)
        markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"tr{:0004d}.tif".format(t))
    '''

if __name__=="__main__":
    main()
