from Visualization import imageReader as ir
from Detection import ctrack
from Detection import convertFiles as cf
from skimage import io

Simulation = False

impath = "SimData/"
images = "SimulatedImages.tif"
if Simulation:
    trackfile = "simulatedTracks.txt"
    particlefile = "simulatedFrames.txt"
    anapath = "SimData/"
else:
    trackfile = "foundTracks.txt"
    trackfile = "foundTracks-SR10.0_20171106-165904.txt"
    trackfile = "foundTracks-SR20.0_20171106-170330.txt"
    trackfile = "foundTracks-SR40.0_20171106-170137.txt"
    particlefile = "foundParticles.txt"
    anapath = "SimData/Analysis/"

images = io.imread(impath+images)

tracks = ctrack.readTrajectoriesFromFile(anapath+trackfile)
print(tracks)
ir.showTracks(images,tracks)

#parts = cf.readDetectedParticles(anapath+particlefile)
#ir.showDetections(impath+images,parts)

