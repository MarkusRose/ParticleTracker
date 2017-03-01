import numpy as np
import Detection.convertFiles as conFiles
import Detection.ctrack as ctrack
import AnalysisTools.driftCorrection as dc
import os
from multiprocessing import Pool, freeze_support
import sys
from time import strftime



#System Parameter
particle_file = "/home/markus/TestTracking/foundParticles.txt"
filelist = [["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundParticles.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundParticles.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundParticles.txt"]]
'''
filelist = [["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt","L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundParticles.txt"]]
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

#Tracking Parameter:
searchRadius = 3
minTracklen = 1
linkRange = 2


def doTrack(particle_file,searchRadius=searchRadius,minTracklen=minTracklen,linkRange=linkRange):
    date = strftime("%Y%m%d-%H%M%S")
    path = os.path.dirname(particle_file)
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    particles = conFiles.readDetectedParticles(particle_file)

    tracks = ctrack.link_particles(particles,searchRadius,link_range=linkRange,min_track_len=minTracklen,outfile="foundTracks-SR{:}_{:}.txt".format(searchRadius,date))

    outfile = open("tracking-SR{:}_{:}.log".format(searchRadius,date),'w')
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

def doTrack_direct(particles, searchRadius=searchRadius,minTracklen=minTracklen,linkRange=linkRange,outfile="foundTracks.txt"):
    date = strftime("%Y%m%d-%H%M%S")

    tracks = ctrack.link_particles(particles,searchRadius,link_range=linkRange,min_track_len=minTracklen,outfile=outfile)#"foundTracks-SR{:}_{:}.txt".format(searchRadius,date))

    outfile = open("tracking-SR{:}_{:}.log".format(searchRadius,date),'w')
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


def track_with_driftcorrect(fn):
    drifttracks = doTrack(fn[1],searchRadius=2)
    pparts = dc.driftCorrection_particles(fn[0],drifttracks)
    path = os.path.dirname(fn[0])
    os.chdir(path)
    conFiles.writeParticleFile(pparts,filename="driftlessParticles.txt")
    date = strftime("%Y%m%d-%H%M%S")
    doTrack_direct(pparts,outfile="driftcorrectedTracks-SR{:}_{:}.txt".format(searchRadius,date))
    return
        


def serial():
    for fn in filelist:
        drifttracks = doTrack(fn[0])
        pparts = dc.driftCorrection_particles(fn[1],drifttracks)
        path = os.path.dirname(fn[1])
        os.chdir(path)
        conFiles.writeParticleFile(pparts,filename="driftlessParticles.txt")
        date = strftime("%Y%m%d-%H%M%S")
        doTrack_direct(pparts,outfile="driftcorrectedTracks-SR{:}_{:}.txt".format(searchRadius,date))
    return

def multiproc():

    freeze_support()
    
    p = Pool(processes = 8)
    results = p.map_async(track_with_driftcorrect,filelist)
    output = results.get()

    return

if __name__=="__main__":
    multiproc()
    #serial()

