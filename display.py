from StagingArea.Visualization import imageReader as ir
from Detection import ctrack

impath = "SimData/SimulatedImages/"
anapath = "SimData/"

images = "SimulatedImages.tif"
trackfile = "simulatedTracks.txt"


tracks = ctrack.readTrajectoriesFromFile(anapath+trackfile)
ir.makeVisual(impath+images,tracks)

