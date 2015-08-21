import numpy as np
from System import Fileio


def createSystemProperties():
    querries = []
    querries.append("Please enter the diffusion coefficient D1 =    [3.0]    ")
    querries.append("Please enter the diffusion coefficient D2 =    [10.0]   ")
    querries.append("Please enter the diffusion coefficient D3 =    [0.0]    ")
    querries.append("Please enter transition probability p12 =      [0.2]    ")
    querries.append("Please enter transition probability p21 =      [0.1]    ")
    querries.append("Please enter transition probability p13 =      [0.1]    ")
    querries.append("Please enter transition probability p23 =      [0.2]    ")
    querries.append("Please enter transition probability p31 =      [0.2]    ")
    querries.append("Please enter transition probability p32 =      [0.1]    ")
    querries.append("How many frames are there?                     [1000]   ")
    querries.append("What is the number of particles?               [1]      ")
    querries.append("What is the acquisition time?                  [0.1]    ")
    querries.append("Number of pixels in one dimension?             [512]    ")
    querries.append("Wavelength?                                    [700]    ")
    querries.append("Pixel size?                                    [16]     ")
    querries.append("NA?                                            [1.54]   ")
    querries.append("Magnification?                                 [100]    ")
    querries.append("S/N?                                           [10]     ")
    querries.append("Intensity?                                     [14000]  ")

    simValues = np.zeros((19))
    simValues[0] = 3.0
    simValues[1] = 10.0
    simValues[2] = 0.0
    simValues[3] = 0.2
    simValues[4] = 0.1
    simValues[5] = 0.1
    simValues[6] = 0.2
    simValues[7] = 0.2
    simValues[8] = 0.1
    simValues[9] = 1000
    simValues[10] = 1  
    simValues[11] = 0.1
    simValues[12] = 512
    simValues[13] = 700
    simValues[14] = 16 
    simValues[15] = 1.54
    simValues[16] = 100
    simValues[17] = 10 
    simValues[18] = 14000


    numD = 1
    while True:
        try: 
            a = raw_input("How many states can the particles occupy? [1] ")
            if a == "":
                break
            else:
                a = int(a)
                numD = a
                if numD > 3 or numD < 1:
                    print "Not a valid state please select an integer between 1 and 3"
                    continue
                break
        except ValueError:
            print "Not an integer, please try again."


    for i in xrange(len(querries)):
        if numD == 1:
            if i in [1,2,3,5,6,8]:
                simValues[i] = 0
                continue
            elif i in [4,7]:
                simValues[i] = 1
                continue
        elif numD == 2:
            if i in [2,5,6,7,8]:
                simValues[i] = 0
                continue
        elif numD ==3:
            pass
        else:
            print "Number of D not allowed."
            break
        while True:
            try:
                a = raw_input(querries[i])
                if a == "":
                    break
                elif i in [9,10,12]:
                    a = int(a)
                    simValues[i] = a
                else:
                    a = float(a)
                    simValues[i] = a
                break
            except ValueError:
                print("Not a float, please try again.")

    Fileio.setSysProps(simValues)

if __name__=="__main__":
    createSystemProperties()
