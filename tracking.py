import numpy as np
import Detection.convertFiles as conFiles
import Detection.ctrack as ctrack
import AnalysisTools.driftCorrection as dc
import os
from multiprocessing import Pool, freeze_support
import sys
from time import strftime



#System Parameter
particle_file = "Not Defined"
'''
filelist = [["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt"]]
        '''

#filelist =  [["/media/markus/DataPartition/SimulationData/C-1-AnalyzedData/foundParticles.txt",
#    "/media/markus/DataPartition/SimulationData/C-1-AnalyzedData/foundParticles.txt"]]

#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li24/foundParticles.txt"
#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li22/foundParticles.txt"
#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li27/foundParticles.txt"
#pfile = "/media/markus/DataPartition/SimulationData/AnalyzedData-Li30/foundParticles.txt"

#Tracking Parameter:
searchRadius = 20
minTracklen = 1
linkRange = 2


def doTrack(particle_file,searchRadius=searchRadius,minTracklen=minTracklen,linkRange=linkRange,path="."):
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

def doTrack_direct(particles, searchRadius=searchRadius,minTracklen=minTracklen,linkRange=linkRange,outfile="foundTracks.txt",infilename="Not Defined",path="."):
    date = strftime("%Y%m%d-%H%M%S")

    tracks = ctrack.link_particles(particles,searchRadius,link_range=linkRange,min_track_len=minTracklen,outfile=outfile)#"foundTracks-SR{:}_{:}.txt".format(searchRadius,date))

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


def track_with_driftcorrect(fn,searchRadius,link_range=2):
    #Create drift tracks from positions
    drifttracks = doTrack(fn[1],searchRadius=2,linkRange=link_range)
    #Apply drift correction to feducial markers for verification and save
    pparts = dc.driftCorrection_particles(fn[1],drifttracks)
    path = os.path.dirname(fn[1])
    date = strftime("%Y%m%d-%H%M%S")
    doTrack_direct(pparts,outfile=path+"/driftcorrectedTracksFM-SR{:}_{:}.txt".format(searchRadius,date),infilename=fn[1],linkRange=link_range)
    #Apply drift correction to other channel and save
    path = os.path.dirname(fn[0])
    pparts = dc.driftCorrection_particles(fn[0],drifttracks)
    conFiles.writeParticleFile(pparts,filename=path+"driftlessParticles.txt")
    date = strftime("%Y%m%d-%H%M%S")
    t = doTrack_direct(pparts,outfile=path+"/driftcorrectedTracks-SR{:}_{:}.txt".format(searchRadius,date),infilename=fn[0],linkRange=link_range)
    return t



def serial():
    for fn in filelist:
        track_with_driftcorrect(fn)
    return

def multiproc():

    freeze_support()
    
    p = Pool(processes = 8)
    results = p.map_async(track_with_driftcorrect,filelist)
    output = results.get()

    return

if __name__=="__main__":
    #multiproc()
    #serial()
    doTrack(pfile)


