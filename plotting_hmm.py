import Detection.ctrack as ctrack
import AnalysisTools.driftCorrection as dc
import AnalysisTools.hiddenMarkov as hmm
import matplotlib.pyplot as plt

import os
import sys
import numpy as np

'''
tracklist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"]
        ]

tracklist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"]
        ]
tracklist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"]
        ]
tracklist = [
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel5A-6-22-10/45C/OD06/Experiment3/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"]
        ]
tracklist = [
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR2_20170209-020551.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR2_20170209-020551.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR2_20170209-020552.txt"]
        ]
tracklist = [
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR3_20170208-230952.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR3_20170208-230952.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR3_20170208-230953.txt"]
        ]
tracklist = [
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR5_20170209-160448.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR5_20170209-160448.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR5_20170209-160449.txt"]
        ]
tracklist = [
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment3/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt"],
        ["L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030447.txt",
            "L:/Cel6B-5-26-10/45C/OD1/Experiment4/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030449.txt"]
        ]
tracklist = [
["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030450.txt",
"L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030458.txt"],
["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR1.5_20170209-030458.txt",
"L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR1.5_20170209-030609.txt"]
]
tracklist = [
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR2_20170209-020554.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR2_20170209-020602.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR2_20170209-020602.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR2_20170209-020713.txt"]
        ]
        '''
tracklist = [
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR3_20170208-230954.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR3_20170208-231002.txt"],
        ["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR3_20170208-231002.txt",
            "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR3_20170208-231115.txt"]
        ]
tracklist = [
["L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundTracks-SR5_20170209-160451.txt",
"L:/Cel9A-6-9-10/45C/OD06/Experiment1/C-2-AnalyzedData/foundTracks-SR5_20170209-160459.txt"],
["L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1-AnalyzedData/foundTracks-SR5_20170209-160459.txt",
"L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-2-AnalyzedData/foundTracks-SR5_20170209-160608.txt"]
]

'''
hmmlist = ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius2/hmmAveragedData.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius2/hmmAveragedData.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/HiddenMarkov/SearchRadius2/hmmAveragedData.txt"]
hmmlist = ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius3/hmmAveragedData.txt",
"L:/Cel5A-6-22-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius3/hmmAveragedData.txt",
"L:/Cel5A-6-22-10/45C/OD06/Experiment3/HiddenMarkov/SearchRadius3/hmmAveragedData.txt"]
hmmlist = ["L:/Cel5A-6-22-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius5/hmmAveragedData.txt",
    "L:/Cel5A-6-22-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius5/hmmAveragedData.txt",
    "L:/Cel5A-6-22-10/45C/OD06/Experiment3/HiddenMarkov/SearchRadius5/hmmAveragedData.txt"]
hmmlist = [
        "L:/Cel5A-6-22-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt",
        "L:/Cel5A-6-22-10/45C/OD06/Experiment3/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt"]
hmmlist = [
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/HiddenMarkov/SearchRadius2/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/HiddenMarkov/SearchRadius2/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/HiddenMarkov/SearchRadius2/hmmAveragedData.txt"]
hmmlist = [
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/HiddenMarkov/SearchRadius3/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/HiddenMarkov/SearchRadius3/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/HiddenMarkov/SearchRadius3/hmmAveragedData.txt"]
hmmlist = [
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/HiddenMarkov/SearchRadius5/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/HiddenMarkov/SearchRadius5/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/HiddenMarkov/SearchRadius5/hmmAveragedData.txt"]
hmmlist = [
        "L:/Cel6B-5-26-10/45C/OD1/Experiment1/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment3/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt",
        "L:/Cel6B-5-26-10/45C/OD1/Experiment4/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt"]
hmmlist = [
"L:/Cel9A-6-9-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt",
"L:/Cel9A-6-9-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius1_5/hmmAveragedData.txt"
]
hmmlist = [
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius2/hmmAveragedData.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius2/hmmAveragedData.txt"
        ]
hmmlist = [
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius3/hmmAveragedData.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius3/hmmAveragedData.txt"
        ]
'''
hmmlist = [
        "L:/Cel9A-6-9-10/45C/OD06/Experiment1/HiddenMarkov/SearchRadius5/hmmAveragedData.txt",
        "L:/Cel9A-6-9-10/45C/OD06/Experiment2/HiddenMarkov/SearchRadius5/hmmAveragedData.txt"
        ]


list_of_tracks = []
list_of_hmmdata = []
path = "L:/Cel9A-6-9-10/45C/OD06/HiddenMarkov/"
SR = 5
trackfile = "foundTracks-Cel9A-SR{:}.txt".format(SR)
hmmfile = "hmmAveragedData-Cel9A-SR{:}.txt".format(SR)

def readHMMData(filename):
    infile = open(filename,'r')

    allhmm = []
    header = ""
    for line in infile:
        td = []
        if line[0] == "#":
            header = line[:]
            continue
        saver = line.split()
        for i in xrange(len(saver)):
            if i==8:
                td.append(saver[i])
            else:
                td.append(float(saver[i]))
        allhmm.append(td)
    return allhmm, header


def trackLength(track):

    framestart = -1
    frameend = -1

    for part in track.track:
        if np.isnan(part['frame']) or part['frame'] == 0:
            continue
        elif framestart == -1:
            framestart = part['frame']
        else:
            frameend = part['frame']
    if framestart == -1:
        return 0
    elif frameend == -1:
        return 1
    return frameend - framestart



if __name__=="__main__":

    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)

    if os.path.isfile(hmmfile):
        print("File '{:}' already exists!".format(hmmfile))
        sys.exit(-1)
    if os.path.isfile(trackfile):
        print("File '{:}' already exists!".format(trackfile))
        sys.exit(-1)


    print("Reading Files")
    sys.stdout.flush()
    for i in xrange(len(hmmlist)):
        drifttracks,driftlist = ctrack.readTrajectoriesFromFile(tracklist[i][1])
        part_tracks,part_list = ctrack.readTrajectoriesFromFile(tracklist[i][0])
        hmmdata,header = readHMMData(hmmlist[i])

        
        pt = dc.driftCorrection(part_tracks,drifttracks)

        list_of_tracks += list(pt)
        list_of_hmmdata += list(hmmdata)
    print("Done. \n")
    sys.stdout.flush()

    ctrack.writeTrajectories(list_of_tracks,filename=trackfile)

    print("Adding Track-length.")
    sys.stdout.flush()
    print("HMM: {:}".format(len(list_of_hmmdata)))
    print("Tracks: {:}".format(len(list_of_tracks)))
    sys.stdout.flush()

    counter = 0
    for i in xrange(len(list_of_hmmdata)):
        for j in xrange(len(list_of_tracks)):
            if list_of_hmmdata[i][8] == list_of_tracks[j].id:
                list_of_hmmdata[i].insert(8,trackLength(list_of_tracks[j]))
                counter += 1
    print counter

    if counter != len(list_of_hmmdata):
        print("Error in number of tracks and lengths!")
        sys.exit(1)

    outthetaf = open(hmmfile,'w')
    outthetaf.write("#  D1 D2 p12 p21 stds: D1 D2 p12 p21 length  particle-ID\n")
    for line in list_of_hmmdata:
        for elem in line:
            outthetaf.write("{:} ".format(elem))
        outthetaf.write("\n")
    outthetaf.close()


    
