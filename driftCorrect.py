import AnalysisTools.driftCorrection as dc
import Detection.ctrack as ctrack
import Detection.convertFiles as conFiles
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
import numpy as np
import tracking


print("Hello World!")

driftfile = "/media/markus/DataPartition/SimulationData/C-1-AnalyzedData/foundTracks-SR2_20170310-231736.txt"
trackfile = "/media/markus/DataPartition/SimulationData/C-1-AnalyzedData/foundTracks-SR2_20170310-231736.txt"
positionfile = "/media/markus/DataPartition/SimulationData/C-1-AnalyzedData/foundParticles.txt"

drifttracks,driftlist = ctrack.readTrajectoriesFromFile(driftfile)
part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)

pt = dc.driftCorrection_tracks(part_tracks,drifttracks)
pparts = dc.driftCorrection_particles(positionfile,drifttracks)


#write drift corrected particles
path = os.path.dirname(positionfile)
if not os.path.isdir(path):
    os.mkdir(path)
os.chdir(path)

tracks = tracking.doTrack_direct(pparts,searchRadius=5)
conFiles.writeParticleFile(pparts,filename="driftlessParticles.txt")


#PLOT THE DRIFT CORRECTED FEDUCIALS
#drift
spng = os.path.join(path,"Drift")
if not os.path.isdir(spng):
    os.mkdir(spng)
os.chdir(spng)

pixel_size = 0.067

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
    plt.savefig("cd{:}.png".format(counter))
    #plt.draw()
    plt.close(fig3)
    print("Done {:}-{:}".format(0,counter))

    fig2 = plt.figure()
    ax = fig2.add_subplot(111)
    ax.plot(z,(x-x.mean())*1000,label="xcoord")
    ax.plot(z,(y-y.mean())*1000,label="ycoord")
    ax.set_xlabel(r'time in $s$')
    ax.set_ylabel(r'movement in $nm$')
    plt.legend()
    plt.savefig("xydim{:}.png".format(counter))
    plt.close(fig2)


