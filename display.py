from StagingArea.Visualization import imageReader as ir
from Detection import ctrack
from Detection import convertFiles as cf

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


tracks = ctrack.readTrajectoriesFromFile(anapath+trackfile)
ir.showTracks(impath+images,tracks)

#parts = cf.readDetectedParticles(anapath+particlefile)
#ir.showDetections(impath+images,parts)

