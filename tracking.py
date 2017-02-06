import numpy as np
import Detection.convertFiles as conFiles
import Detection.ctrack as ctrack
import os



#System Parameter
particle_file = "/home/markus/TestTracking/foundParticles.txt"
#Tracking Parameter:
searchRadius = 3
minTracklen = 1







if __name__=="__main__":
    path = os.path.dirname(particle_file)
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    particles = conFiles.readDetectedParticles(particle_file)

    tracks = ctrack.link_particles(particles,searchRadius,minTracklen,outfile="foundTracks-SR{:}.txt".format(searchRadius))


