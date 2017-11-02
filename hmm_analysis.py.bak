import numpy as np
import sys
import os
from multiprocessing import Pool, freeze_support

import AnalysisTools.driftCorrection as dc
import AnalysisTools.hiddenMarkov as hmm
import Detection.ctrack as ctrack

SR = 3

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
'''
filelist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR3_20170208-230953.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230954.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-231002.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR3_20170208-231002.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR3_20170208-231115.txt"]
        ]
'''
'''
filelist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030449.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030450.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030458.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030458.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030609.txt"]
        ]
'''
'''
filelist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR5_20170209-160449.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160451.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160459.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR5_20170209-160459.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR5_20170209-160608.txt"]
        ]
'''
filelist = [ 
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183759.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183759.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183759.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183800.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183809.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183801.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183759.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/driftcorrectedTracks-SR3_20170224-183759.txt"
        ]


def serial():
    for fn in filelist:
        hmm.doHMM(fn,montecarlo=10000,SR=SR)
    return

def multiproc():

    freeze_support()
    
    p = Pool(processes = 8)
    results = p.map_async(hmm.doHMM,filelist)
    output = results.get()

    return

if __name__=="__main__":
    #serial()
    multiproc()


