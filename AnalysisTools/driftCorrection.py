import Detection.ctrack as ctrack
import Detection.convertFiles as conFiles
import Detection.detectParticles as dpart
import numpy as np
import sys
import os
from time import strftime

#correct for rotation of Sample on tracks
def rotationCorrection_tracks(part_tracks,drifttracks):
    return



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
        for i in range(tracklen):
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

    for i in range(len(contribnum)):
        drift_displ.track[i]['x'] /= contribnum[i]
        drift_displ.track[i]['y'] /= contribnum[i]

    for track in part_tracks:
        for i in range(len(track.track)):
            if not np.isnan(drift_displ.track[i]['x']) and not np.isnan(drift_displ.track[i]['y']):
                track.track[i]['x'] -= drift_displ.track[i]['x']
                track.track[i]['y'] -= drift_displ.track[i]['y']

    return part_tracks

#correct for rotation of Sample on particle positions
def rotationCorrection_particles(drifttracks):
    
    tracklen = len(drifttracks[0].track)
    angles = np.zeros((len(drifttracks),tracklen),dtype=np.float)
    for i in range(1,len(drifttracks),1):
        for j in range(tracklen):
            dx = drifttracks[i].track[j]['x'] - drifttracks[0].track[j]['x']
            dy = drifttracks[i].track[j]['y'] - drifttracks[0].track[j]['y']
            angles[i,j] = dy/dx
    angles = np.arctan(angles)
    anglecorrection = angles[1:,1:] - angles[1:,:-1]

    return anglecorrection.mean(axis=0), drifttracks[0].track[['x', 'y']]

def translationCorrection_particles(drifttracks):
    tracklen = len(drifttracks[0].track)
    drift_displ = ctrack.ParticleTrack(id=1,num_elements=tracklen)
    contribnum = np.zeros(tracklen)

    for track in drifttracks[:min(1,len(drifttracks))]:
        x = np.nan
        x_start = np.nan
        y = np.nan
        y_start = np.nan
        firstelement = True
        for i in range(tracklen):
            x = track.track[i]['x']
            y = track.track[i]['y']

            #USING previous as reference
            if np.isnan(x_start) and np.isnan(y_start):
                x_start = x
                y_start = y
            else:
                if x != np.nan and y != np.nan:
                    if np.isnan(drift_displ.track[i]['x']) and np.isnan(drift_displ.track[i]['y']):
                        drift_displ.track[i]['x'] = (x - x_start)
                        drift_displ.track[i]['y'] = (y - y_start)
                    else:
                        drift_displ.track[i]['x'] += x - x_start
                        drift_displ.track[i]['y'] += y - y_start
                    contribnum[i] += 1

            ''' 
            #USING 0 AS REF
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
            '''

    for i in range(len(contribnum)):
        drift_displ.track[i]['x'] /= contribnum[i]
        drift_displ.track[i]['y'] /= contribnum[i]
        drift_displ.track[i]['frame'] = i+1

    return drift_displ


#create Drift correction on Particle Positions
def driftCorrection_particles(part_positions,drifttracks,rotcorrection=True):

    tracklen = len(drifttracks[0].track)
    if len(part_positions) != tracklen:
        print("Error: !!!Tracks don't have same length!!!")
        sys.exit(1)

    drift_displ = translationCorrection_particles(drifttracks)
    angle_change, rotcenter = rotationCorrection_particles(drifttracks)

    
    for i in range(1,len(part_positions)):
        count = 0
        for part in part_positions[i]:
            if not np.isnan(angle_change[i-1]) and rotcorrection:
                l = np.sqrt((part.x - rotcenter[i]['x'])**2 + (part.y - rotcenter[i]['y'])**2)
                phi = np.arctan((part.y - rotcenter[i]['y'])/(part.x - rotcenter[i]['x']))
                factor = np.sign(part.x - rotcenter[i]['x'])
                part.x = rotcenter[i]['x'] + factor * l * np.cos(phi - angle_change[i-1])
                part.y = rotcenter[i]['y'] + factor * l * np.sin(phi - angle_change[i-1])
            if not np.isnan(drift_displ.track[i]['x']) and not np.isnan(drift_displ.track[i]['y']):
                part.x -= drift_displ.track[i]['x']
                part.y -= drift_displ.track[i]['y']

    return part_positions

def doTrack(particle_file,searchRadius=2,minTracklen=1,linkRange=2):
    date = strftime("%Y%m%d-%H%M%S")
    path = os.path.dirname(particle_file)
    particles = conFiles.readDetectedParticles(particle_file)

    tracks = ctrack.link_particles(particles,searchRadius,link_range=linkRange,min_track_len=minTracklen,outfile=path+"/foundTracks-SR{:}_{:}.txt".format(searchRadius,date))

    outfile = open(path+"/tracking-SR{:}_{:}.log".format(searchRadius,date),'w')
    timestr = strftime("%Y-%m-%d %H:%M:%S")

    outfile.write("Tracking Log File\n==================\n\n")
    outfile.write("Time:   {:}\n".format(timestr))
    outfile.write("\nSystem Parameters:\n------------------\n")
    outfile.write("Particle File:   {:}\n".format(particle_file))
    outfile.write("\nTracking Parameters:\n---------------------\n")
    outfile.write("Search Radius = {:}px\n".format(searchRadius))
    outfile.write("Link Range = {:} frames\n".format(linkRange))
    outfile.write("Minimum Track Length = {:} frame(s)\n".format(minTracklen))
    outfile.write("\n=== Track-IDs =================\n")
    for track in tracks:
        outfile.write("{:}\n".format(track.id))
    outfile.close()

    return tracks

def doTrack_direct(particles, searchRadius=2,minTracklen=1,linkRange=2,outfile="foundTracks.txt",infilename="Not Defined",path="."):
    date = strftime("%Y%m%d-%H%M%S")

    tracks = ctrack.link_particles(particles,searchRadius,link_range=int(linkRange),min_track_len=minTracklen,outfile=path+'/'+outfile)#"foundTracks-SR{:}_{:}.txt".format(searchRadius,date))

    outfile = open(path+"/tracking-SR{:}_{:}.log".format(searchRadius,date),'w')
    timestr = strftime("%Y-%m-%d %H:%M:%S")

    outfile.write("Tracking Log File\n==================\n\n")
    outfile.write("Time:   {:}\n".format(timestr))
    outfile.write("\nSystem Parameters:\n------------------\n")
    outfile.write("Particle File:   {:}\n".format(infilename))
    outfile.write("\nTracking Parameters:\n---------------------\n")
    outfile.write("Search Radius = {:}px\n".format(searchRadius))
    outfile.write("Link Range = {:} frames\n".format(linkRange))
    outfile.write("Minimum Track Length = {:} frame(s)\n".format(minTracklen))
    outfile.write("\n=== Track-IDs =================\n")
    for track in tracks:
        outfile.write("{:}\n".format(track.id))
    outfile.close()

    return tracks

#Do driftcorrect on detected particles.
def position_with_driftcorrect(fn,path='.'):
    #Create drift tracks from positions
    drifttracks = doTrack_direct(fn[1],searchRadius=2,linkRange=2,outfile='driftTracks.txt',path=path)
    #Apply drift correction to feducial markers for verification and save
    #pparts = driftCorrection_particles(fn[1],drifttracks)
    #path = os.path.dirname(fn[1])
    #date = strftime("%Y%m%d-%H%M%S")
    #doTrack_direct(pparts,outfile=path+"/driftcorrectedTracksFM-SR{:}_{:}.txt".format(2,date),infilename=fn[1],linkRange=link_range)
    #Apply drift correction to other channel and save
    #path = os.path.dirname(fn[0])
    print("Correcting for Drift now")
    sys.stdout.flush()
    pparts = driftCorrection_particles(fn[0],drifttracks)
    conFiles.writeParticleFile(pparts,filename=path+"/driftlessParticles.txt")
    print("Done!")
    sys.stdout.flush()
    return pparts

#Do drift correct on detected particles and track them afterwards
def track_with_driftcorrect(fn,searchRadius,link_range=2,path='.'):
    #Create drift tracks from positions
    drifttracks = doTrack_direct(fn[1],searchRadius=2,linkRange=2,outfile='driftTracks.txt',path=path)
    #Apply drift correction to feducial markers for verification and save
    '''
    pparts = driftCorrection_particles(fn[1],drifttracks)
    path = os.path.dirname(fn[1])
    date = strftime("%Y%m%d-%H%M%S")
    doTrack_direct(pparts,outfile=path+"/driftcorrectedTracksFM-SR{:}_{:}.txt".format(2,date),infilename=fn[1],linkRange=link_range)
    #Apply drift correction to other channel and save
    path = os.path.dirname(fn[0])
    '''
    print("Correcting for Drift now")
    sys.stdout.flush()
    pparts = driftCorrection_particles(fn[0],drifttracks)
    conFiles.writeParticleFile(pparts,filename=path+"driftlessParticles.txt")
    date = strftime("%Y%m%d-%H%M%S")
    t = doTrack_direct(pparts,outfile="driftcorrectedTracks-SR{:}_{:}.txt".format(searchRadius,date),infilename=fn[0],linkRange=link_range,path=path)
    return t



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
    
    conFiles.writeParticleFile(pparts,filename=path+"/driftlessParticles.txt")




