import Simulation.enzymeDiffuser as enzD
import Simulation.simSetup as simSetup
import multiprocessing as mp
from System import Fileio
import numpy as np
import os
import sys


def runSimulation(simulationVariables,path='.'):
    print("{:} - Process {:8d}".format(mp.current_process().name,os.getpid()))
    print("Path = {:}".format(path))
    print("D1 = {:2.02e}".format(simulationVariables[1]))
    print("D2 = {:2.02e}".format(simulationVariables[2]))
    print("p12 = {:2.02e}".format(simulationVariables[4]))
    print("p21 = {:2.02e}".format(simulationVariables[5]))
    sys.stdout.flush()

    if not os.path.isdir(path):
        os.mkdir(path)
    
    Fileio.setSysProps(simulationVariables,path=path)
    enzD.simulateTracks(inVars=simulationVariables,path=path,imageoutput=True)

    return


if __name__=="__main__":
    simulationPath = 'L:\Markus\TwoStateSimulation'
    if not os.path.isdir(simulationPath):
        os.mkdir(simulationPath)

    simValues = np.zeros((21))
    simValues[0] = 2        # Number of states
    simValues[1] = 1e-3     # D1
    simValues[2] = 1e-4     # D2
    simValues[3] = 0        # D3
    simValues[4] = 0.3      # p12
    simValues[5] = 0.1      # p21
    simValues[6] = 0        # p13
    simValues[7] = 0        # p23
    simValues[8] = 0        # p31
    simValues[9] = 0        # p32
    simValues[10] = 100     # Num Frames
    simValues[11] = 300     # Num Particles
    simValues[12] = 1       # frame interval tau
    simValues[13] = 512     # num pixels
    simValues[14] = 700     # wavelength
    simValues[15] = 0.067   # pixel size
    simValues[16] = 1.45    # NA numerical aperture
    simValues[17] = 1000    # Background average
    simValues[18] = 700     # Background noise
    simValues[19] = 3000    # Intensity
    simValues[20] = False   # Blinking

    taskQ = mp.Queue();

    for p12 in [0.1,0.3,0.5]:
        simValues[4] = p12
        for D1 in [1e-4,2e-4,5e-4,1e-3]:
            simValues[1] = D1
            taskQ.put([np.array(simValues),os.path.join(simulationPath+"D1-{:}_p12-{:}".format(D1,p12))])

    processes = []
    while not taskQ.empty():
        processes.append(mp.Process(target=runSimulation,args=taskQ.get()))
        processes[-1].start()

    for p in processes:
        p.join()

