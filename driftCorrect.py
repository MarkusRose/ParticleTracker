import AnalysisTools.driftCorrection as dc
import Detection.ctrack as ctrack
import Detection.convertFiles as conFiles
import os

print("Hello World!")

driftfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170224-212537.txt"
trackfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170224-212537.txt"
positionfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt"

drifttracks,driftlist = ctrack.readTrajectoriesFromFile(driftfile)
part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)

pt = dc.driftCorrection_tracks(part_tracks,drifttracks)
pparts = dc.driftCorrection_particles(positionfile,drifttracks)

path = os.path.dirname(positionfile)
if not os.path.isdir(path):
    os.mkdir(path)
os.chdir(path)

conFiles.writeParticleFile(pparts,filename="driftlessParticles.txt")

