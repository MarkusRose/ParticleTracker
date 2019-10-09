import numpy as np
from System import Fileio


def createSystemProperties(path = '.'):
    querries = []
    querries.append("Enter the number of states =                   [2]      ")
    querries.append("Please enter the diffusion coefficient D1 =    [1e-3]   ")
    querries.append("Please enter the diffusion coefficient D2 =    [1e-4]   ")
    querries.append("Please enter the diffusion coefficient D3 =    [0]      ")
    querries.append("Please enter transition probability p12 =      [0.3]    ")
    querries.append("Please enter transition probability p21 =      [0.2]    ")
    querries.append("Please enter transition probability p13 =      [0.0]    ")
    querries.append("Please enter transition probability p23 =      [0.0]    ")
    querries.append("Please enter transition probability p31 =      [0.0]    ")
    querries.append("Please enter transition probability p32 =      [0.0]    ")
    querries.append("How many frames are there?                     [100]    ")
    querries.append("What is the number of particles?               [30]     ")
    querries.append("What is the acquisition time?                  [1]      ")
    querries.append("Number of pixels in one dimension?             [512]    ")
    querries.append("Wavelength?                                    [700]    ")
    querries.append("Pixel size?                                    [0.067]  ")
    querries.append("NA?                                            [1.45]   ")
    querries.append("Background level                               [1000]   ")
    querries.append("Background noise                               [700]    ")
    querries.append("Intensity?                                     [3000]   ")
    querries.append("Blinking?                (True = 1, False = 0) [0]      ")

    simValues = np.zeros((21))
    simValues[0] = 2
    simValues[1] = 1e-3
    simValues[2] = 1e-4
    simValues[3] = 0
    simValues[4] = 0.3
    simValues[5] = 0.2
    simValues[6] = 0
    simValues[7] = 0
    simValues[8] = 0
    simValues[9] = 0
    simValues[10] = 100
    simValues[11] = 30
    simValues[12] = 1
    simValues[13] = 512
    simValues[14] = 700
    simValues[15] = 0.067
    simValues[16] = 1.45
    simValues[17] = 1000
    simValues[18] = 700
    simValues[19] = 3000
    simValues[20] = False


    for i in range(len(querries)):
        if i == 0:
            while True:
                try:
                    a = input(querries[0])
                    simValues[0] = int(a)
                    break
                except ValueError:
                    print("Not a float, please try again.")
            if simValues[0] == 1:
                numD = 1
                continue
            elif simValues[0] == 2:
                numD = 2
                continue
            else:
                print("Number of states not allowed.")
                sys.exit()
        if numD == 1:
            if i in [2,3,4,6,7,9]:
                simValues[i] = 0
                continue
            elif i in [5,8]:
                simValues[i] = 1
                continue
        elif numD == 2:
            if i in [3,6,7,8,9]:
                simValues[i] = 0
                continue
        else:
            print("Number of D not allowed.")
            sys.exit()
            break
        while True:
            try:
                a = input(querries[i])
                if a == "":
                    break
                elif i in [10,11,13,20]:
                    a = int(a)
                    simValues[i] = a
                else:
                    a = float(a)
                    simValues[i] = a
                break
            except ValueError:
                print("Not a float, please try again.")
        if i == 20:
            if simValues[20] == 1:
                simValues[20] = True
            elif simValues[20] == 0:
                simValues[20] = False
            else:
                simValues[20] = False
                print("Wrong value for blinking status. Changed to 0.")

    Fileio.setSysProps(simValues,path=path)
    return simValues


if __name__=="__main__":
    createSystemProperties()


