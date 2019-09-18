import numpy as np
import sys
import os
from multiprocessing import Pool, freeze_support

import AnalysisTools.driftCorrection as dc
import AnalysisTools.hiddenMarkov as hmm
import Detection.ctrack as ctrack


'''
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
        '''


def serial(filelist):
    for fn in filelist:
        hmm.doHMM(fn,montecarlo=100000,minTrLength=20,ViewLive=False)
    return

def multiproc():

    freeze_support()
    
    p = Pool(processes = 8)
    results = p.map_async(hmm.doHMM,filelist)
    output = results.get()

    return

if __name__=="__main__":
    filelist = []
    if len(sys.argv) > 1 :
        filelist = sys.argv[1:]
    serial(filelist)
    #multiproc()


