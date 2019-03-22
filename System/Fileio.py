#==================================
#===   File in-/output
#==================================

'''
This script reads and generates the 4 used filetypes in this
program. It contains getter and setter functions for each type.
'''

from PIL import Image
import math
import random
import os
import sys
import csv

import numpy as np
from skimage import io
import copy


#System Properties
#-----------------
#The input parameters have to be of the shape:
'''
(D1, D2, D3, p12, p21, p13, p23, p31, p32,
 number of frame, number of particles, acquisition time, pixel array,
 wavelength, Pixel size, NA, magnification, S/N, Intensity)
'''
#setter
def setSysProps(paramArray):
    outfile = open("SystemParameters.txt",'w')
    outfile.write("#System Parameteres for [Program]\n")
    outfile.write("#\n")

    outfile.write("#Number of diffusion states: \n" )
    outfile.write(str(paramArray[0])+"\n\n")

    outfile.write("#Diffusion constants [D1, D2, D3] (um^2/s)\n")
    for i in range(1,4,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Transition probabilities [p12, p21, p13, p23, p31, p32]\n")
    for i in range(4,10,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Imaging properties [numFrames, numParticles, tau (ms), numPixels-1d]\n")
    for i in range(10,14,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Camera Properties [lambda (nm), pixel size (um)]\n")
    for i in range(14,16,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Microscope Properties [NA, magnification, Background, Backnoise, Intensity (#photons)\n")
    for i in range(16,21,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#EOF\n")
    
    outfile.close()
    return
    


#getter
def getSysProps():
    pA = []
    infile = open("SystemParameters.txt",'r')
    for line in infile:
        if len(line) == 0 or line[0] == "#":
            continue
        else:
            k = line.split()
            for i in k:
                if i == "n/a":
                    pA.append(-1)
                    print("n/a found")
                else:
                    pA.append(float(i))
    return pA

#Frame-by-frame Detection
#------------------------
#The input parameters have to be of the shape:
'''
All Frames = [Frame1,Frame2,Frame3,...]
Framei = [Particle1, Particle2, ...]
Particle1 = [frame, x, y, delta_x, delta_y, Intensity, 
 Background, sigma_x, sigma_y, Particle ID]
So: All Frames = [[[],[],...],[[],[],...],....]
'''
#setter
def setDetection(detParts,filename="DetectedParticles.txt"):
    outfile = open(filename,'w')
    outfile.write("#Frame-by-frame list of detected particles\n")

    for frame in range(len(detParts)):
        outfile.write("\n")
        outfile.write("#Frame "+str(frame+1)+":\n")
        outfile.write("#Frame  X_pos  Y_pos  X_err  Y_err  Intensity  Background  sigma_X  sigma_Y  ParticleID\n")
        for particle in detParts[frame]:
            for prop in particle:
                outfile.write(str(prop) + " ")
            outfile.write("\n")
        outfile.write("\n")

    outfile.close()                        
    return

#getter
def getDetection():
    ffdets = []
    frame = []
    particle = []
    infile = open("DetectedParticles.txt",'r')
    openTrack = 0
    for line in infile:
        if line[0] == '#':
            continue
        elif line[0] == "\n":
            if openTrack == 0:
                openTrack = 1
            else:
                ffdets.append(frame)
                frame = []
                openTrack = 0
        else:
            for elem in line.split():
                particle.append(float(elem))
            frame.append(particle)
            particle = []
                
    return ffdets

#Individual Tracks
#-----------------
#The input parameters have to be of the shape:
'''
All Tracks = [Track1,Track2,Track3,...]
Tracki = [Particle1, Particle2, ...]
Particle1 = [frame, dx, dy, x, y, state, Intensity, 
 Background, sigma_x, sigma_y, Particle ID]
'''
#setter
def setTrackFile(detTracks,filename="foundTracks.txt"):
    outfile = open(filename,'w')
    outfile.write("#All found tracks\n")

    for track in range(len(detTracks)):
        outfile.write("\n")
        outfile.write("#Track "+str(track+1)+":\n")
        outfile.write("#Frame  dX  dY  X_pos  Y_pos  State  Intensity  Background  sigma_X  sigma_Y  ParticleID\n")
        #print detTracks[track]
        for particle in detTracks[track]:
            for prop in particle:
                outfile.write(str(prop) + " ")
            outfile.write("\n")
        outfile.write("\n")

    outfile.close()                        
    return

def writeTrackCSV(tracks):
    with open("foundTracks.csv",'w') as csvfile:
        csvwriter = csv.writer(csvfile,delimiter=',')
        head = ["Frame","dX","dY","X_pos","Y_pos","State","Intensity","Background","sigma_X","sigma_Y","ParticleID"]
        csvwriter.writerow(head)
        for track in tracks:
            csvwriter.writerows(track)
    return
        

#getter
def getTrackFile():
    alltracks = []
    track = []
    particle = []
    infile = open("foundTracks.txt",'r')
    openTrack = 0
    for line in infile:
        if line[0] == '#':
            continue
        elif line[0] == "\n":
            if openTrack == 0:
                openTrack = 1
            else:
                alltracks.append(track)
                track = []
                openTrack = 0
        else:
            for elem in line.split():
                particle.append(float(elem))
            track.append(particle)
            particle = []
                
    return alltracks

def readTrackCSV(tracks):
    with open("foundTracks.csv",'r') as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',')
        alltracks = []
        inarray = []
        next(csvreader)
        for row in csvreader:
            inarray.append(np.array(list(map(float,row))))

        part_id = inarray[0][-1]
        print(part_id)
        track = []
        for part in inarray:
            if part[-1] != part_id:
                alltracks.append(list(track))
                part_id = part[-1]
                track = []
            else:
                track.append(part)
        if len(track) != 0:
            alltracks.append(list(track))
            track = []
        
        return alltracks


#Convert Tracks to Frames
#------------------------
def tracksToFrames(alltracks):
    max = len(alltracks[0])
    for i in range(1,len(alltracks),1):
        if max < len(alltracks[i]):
            max = len(alltracks[i])
    
    allframes = []
    for k in range(max):
        frame = []
        for i in range(len(alltracks)):
            for j in range(len(alltracks[i])):
                if alltracks[i][j][0] == k:
                    part = []
                    for v in range(len(alltracks[i][j])):
                        if v in [0,3,4,6,7,8,9,10]:
                            part.append(alltracks[i][k][v])
                            if v == 4:
                                part.append(0.0)
                                part.append(0.0)
                    frame.append(list(part))
        allframes.append(copy.deepcopy(frame))

    return allframes


    
#Read and write tiff Images
#--------------------------
#setter
'''First we have to read the image'''
def readImage(imagepath):
    inImage = Image.open(imagepath)
    bit_depth = 16
    if inImage.mode == 'L':
        bit_depth = 8
    elif inImage.mode == 'I;16':
        bit_depth = 16
    else:
#        print("Bit_depth unknown, set to 16bit")
        bit_depth = 16

#    print inImage.size
    a = np.asarray(inImage.getdata())
#    print a.shape
    a = np.resize(a.astype(float),(inImage.size[1],inImage.size[0]))
#    print a.shape
    return adjustRange(a,bit_depth)


'''
Image is not read as unsigned integer, so range is [-2^(bit/2),(2^(bit/2)-1)]
Range must be adjusted to [0,2^(bit)-1]
'''
def adjustRange(image,bit_depth):
    '''
    print(image.min())
    print
    '''
    for i in range(len(image)):
        for j in range(len(image[i])):
            if image[i,j] < 0:
                #print(image.min())
                image[i,j] = 65536 + image[i,j]
                #print(image.min())
    '''
    print
    print(image.min())
    '''
    return image/(1.0*(2**bit_depth))

def setImages():
    print("Hello World!")

#getter
def getImages():
    pass

def makeImage(positions,framenumber,dirname,numPixels,sigma,background,backnoise):
    data = np.zeros((numPixels,numPixels),np.uint16)
     
    def gauss(i,j,posx,posy,intensity,sig):
        return math.exp(-((i-posx)**2+(j-posy)**2)/(2.0*sig**2))*intensity

    def integauss(i,j,posx,posy,intensity,sig):
        #int_i^(i+1) int_j^(j+1) dx dy exp(-((i-posx)^2+(j-posy)^2)/2*sig^2) * intensity
        px = (math.erf((posx-i)/(math.sqrt(2)*sig))-math.erf((posx-i-1)/(math.sqrt(2)*sig)))
        py = (math.erf((posy-j)/(math.sqrt(2)*sig))-math.erf((posy-j-1)/(math.sqrt(2)*sig)))
        return intensity/4*px*py

    def noise():
        return random.gauss(background,backnoise)

    intensity = 0
    for k in range(len(positions)):
        px = int(round(positions[k].y))
        py = int(round(positions[k].x))
        intensity += positions[k].amplitude
        #xnum = min(len(data)-1,px+10)-max(0,px-10)
        #ynum = min(len(data[0])-1,py+10)-max(0,py-10)
        for i in range(max(0,px-30),min(len(data)-1,px+30),1):
            for j in range(max(0,py-30),min(len(data[i])-1,py+30),1):
                msig = gauss(i,j,positions[k].y,positions[k].x,positions[k].amplitude,sigma)
                if msig >= 2**16:
                    msig = 2**16-1
                elif msig < 0:
                    msig = 0
                data[i][j] += msig
                if data[i][j] >= 2**16:
                    data[i][j] = 2**16-1
                elif data[i][j] < 0:
                    data[i][j] = 0
    
    if backnoise > 0:
        if True:
            msig = np.random.normal(loc=background,scale=backnoise,size=data.shape)
            np.clip(data+msig,0,2**16-1,data)
        else:
            for i in range(len(data)):
                for j in range(len(data[i])):
                    msig = np.random.normal(background,backnoise)
                    if msig >= 2**16:
                        msig = 2**16 -1
                    elif msig < 0:
                        msig = 0
                    data[i][j] += msig
    else:
        msig = np.zeros(data.shape,np.uint16)

        msig.fill(background)
        np.clip(data+msig,0,2**16-1,data)
    
    #h,w = data.shape
    # 
    #im = Image.frombytes('I;16',(w,h),data.tostring())
    #im.save(dirname+'/frame{0:04d}.tif'.format(framenumber))
    
    return data


def createImages(dirname,frames,numPixels,sigma,background,backnoise):
    try:
        a = "N"
        #a = raw_input("Careful, deleting files. Abort? [Y]/n     ")
        if a == "Y" or a == "y":
            sys.exit(0)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
    except:
        pass
    print("creating images now")
    sys.stdout.flush()

    outarray = []
    for i in range(len(frames)):
        outarray.append(makeImage(frames[i],i,dirname,numPixels,sigma,background,backnoise))
    io.imsave(dirname + "/" + "SimulatedImages.tif",np.array(outarray))
    return
    

#So this is what there is to be done
'''
still need the images
the rest works
'''


if __name__=="__main__":
    tracks = readTrackCSV("foundTracks.csv")
    print(len(tracks[0]))

