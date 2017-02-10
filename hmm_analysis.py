import numpy as np
import sys
import os
from multiprocessing import Pool, freeze_support

import AnalysisTools.driftCorrection as dc
import AnalysisTools.hiddenMarkov as hmm
import Detection.ctrack as ctrack


filelist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR2_20170209-020552.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020554.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020602.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR2_20170209-020602.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR2_20170209-020713.txt"]
        ]

def doHMM(filelist,montecarlo=10000,subfolder="SearchRadius2"):
    trackfile = filelist[0]
    driftfile = filelist[1]

    drifttracks,driftlist = ctrack.readTrajectoriesFromFile(driftfile)
    part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)

    path = os.path.abspath(os.path.join(os.path.dirname(trackfile), '..', 'HiddenMarkov'))
    subpath = os.path.abspath(os.path.join(path,subfolder))
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(subpath):
        os.mkdir(subpath)
    os.chdir(subpath)

    print path
    sys.stdout.flush()

    print("Doing Drift Correction")
    sys.stdout.flush()

    pt = dc.driftCorrection(part_tracks,drifttracks)

    print("Running HMM")
    sys.stdout.flush()

    thetas = hmm.runHiddenMarkov(pt,MCMC=montecarlo)
    thetas = []

    return thetas


def serial():
    for fn in filelist:
        doHMM(fn)
    return

def multiproc():

    freeze_support()
    
    p = Pool(processes = 8)
    results = p.map_async(doHMM,filelist)
    output = results.get()

    return

if __name__=="__main__":
    #serial()
    multiproc()


