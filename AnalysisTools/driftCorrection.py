import Detection.ctrack as ctrack
import Detection.convertFiles as conFiles
import Detection.detectParticles as dpart
import numpy as np
import sys



#create Drift correction on Trajectories
def driftCorrection_tracks(part_tracks,drifttracks):

    tracklen = len(drifttracks[0].track)
    for tr in part_tracks:
        if len(tr.track) != tracklen:
            print("Error: !!!Tracks don't have same length!!!")
            sys.exit(1)

    drift_displ = ctrack.ParticleTrack(id=1,num_elements=tracklen)
    contribnum = np.zeros(tracklen)

    for track in drifttracks:
        x = np.nan
        x_start = np.nan
        y = np.nan
        y_start = np.nan
        firstelement = True
        for i in xrange(tracklen):
            x = track.track[i]['x']
            y = track.track[i]['y']
            if firstelement:
                if not np.isnan(x) and not np.isnan(y):
                    x_start = x
                    y_start = y
                    firstelement = False
                else:
                    continue
            else:
                if x != np.nan and y != np.nan:
                    if np.isnan(drift_displ.track[i]['x']) and np.isnan(drift_displ.track[i]['y']):
                        drift_displ.track[i]['x'] = (x - x_start)
                        drift_displ.track[i]['y'] = (y - y_start)
                    else:
                        drift_displ.track[i]['x'] += x - x_start
                        drift_displ.track[i]['y'] += y - y_start
                    contribnum[i] += 1

    for i in xrange(len(contribnum)):
        drift_displ.track[i]['x'] /= contribnum[i]
        drift_displ.track[i]['y'] /= contribnum[i]

    for track in part_tracks:
        for i in xrange(len(track.track)):
            if not np.isnan(drift_displ.track[i]['x']) and not np.isnan(drift_displ.track[i]['y']):
                track.track[i]['x'] -= drift_displ.track[i]['x']
                track.track[i]['y'] -= drift_displ.track[i]['y']

    return part_tracks

#create Drift correction on Particle Positions
def driftCorrection_particles(positionfile,drifttracks):

    part_positions = conFiles.readDetectedParticles(positionfile)

    tracklen = len(drifttracks[0].track)
    if len(part_positions) != tracklen:
        print("Error: !!!Tracks don't have same length!!!")
        sys.exit(1)

    drift_displ = ctrack.ParticleTrack(id=1,num_elements=tracklen)
    contribnum = np.zeros(tracklen)

    for track in drifttracks[:min(3,len(drifttracks))]:
        x = np.nan
        x_start = np.nan
        y = np.nan
        y_start = np.nan
        firstelement = True
        for i in xrange(tracklen):
            x = track.track[i]['x']
            y = track.track[i]['y']
            if firstelement:
                if not np.isnan(x) and not np.isnan(y):
                    x_start = x
                    y_start = y
                    firstelement = False
                else:
                    continue
            else:
                if x != np.nan and y != np.nan:
                    if np.isnan(drift_displ.track[i]['x']) and np.isnan(drift_displ.track[i]['y']):
                        drift_displ.track[i]['x'] = (x - x_start)
                        drift_displ.track[i]['y'] = (y - y_start)
                    else:
                        drift_displ.track[i]['x'] += x - x_start
                        drift_displ.track[i]['y'] += y - y_start
                    contribnum[i] += 1

    for i in xrange(len(contribnum)):
        drift_displ.track[i]['x'] /= contribnum[i]
        drift_displ.track[i]['y'] /= contribnum[i]
        drift_displ.track[i]['frame'] = i+1

    for i in xrange(1,len(part_positions)):
        for part in part_positions[i]:
            if not np.isnan(drift_displ.track[i]['x']) and not np.isnan(drift_displ.track[i]['y']):
                part.x -= drift_displ.track[i]['x']
                part.y -= drift_displ.track[i]['y']

    return part_positions



if __name__=="__main__":

    '''
    driftfile = "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR2_20170209-020552.txt"
    trackfile = "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt"
    '''
    driftfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"
    trackfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"
    positionfile = "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundPositions.txt"

    drifttracks,driftlist = ctrack.readTrajectoriesFromFile(driftfile)
    part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)
    part_positions = conFiles.readDetectedParticles(positionfile)

    #pt = driftCorrection_tracks(part_tracks,drifttracks)
    pparts = driftCorrection_particles(part_positions,drifttracks)

    path = os.path.dirname(positionfile)
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    
    conFiles.writeParticleFile(pparts,filename="driftlessParticles.txt")




