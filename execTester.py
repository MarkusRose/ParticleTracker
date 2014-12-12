import detectParticles
import readImage
import ctrack
import markPosition
import convertFiles
import analysisTools

import pysm
import sys
import os
import glob
import shutil
from scipy import ndimage
from matplotlib import pyplot as plt
import numpy as np

#==============================
# Global Variables
#==============================
sigma = 1.0
local_max_window = 4
signal_power = 8
bit_depth = 16
eccentricity_thresh = 2
sigma_thresh = 3
max_displacement = 10
addUp = 1
minTrackLen = 1

    
#==============================
# Main Functions
#==============================
def chPath(path):

    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        option = raw_input("    !!! Careful! '"+path+"' exists! !!!\n    !!!    Do you wish to continue? [y,N] ")
        if not (option == "y" or option == "Y" or option == "Yes" or option == "yes" or option == "YES"):
            sys.exit("Data exists already. Quitting now.")
    shutil.copyfile("setup.txt",path+"/setup.txt")
    os.chdir(path)

    return

def readImageList(path):
    if not os.path.isdir(path):
        print "No path named " + path
        raise ValueError, "No path named " + path
    img = glob.glob(os.path.join(path, '*.tif'))
    print "Number of images found: " + str(len(img))
    return img

def dataCorrect(particle_data):
    frame_count = 0
    output = True
    for frame in particle_data:
        frame_count += 1
        for particle in frame:
            #print particle.frame, addUp, frame_count
            if particle.frame != frame_count+addUp-1:
                output = False
                print ("nope, particle aint in right frame.")
                break
        if not output:
            break
    return output 

def makeFirstImage(img,lm=None):
    inimage = img[0:addUp]
    particle_data = detectParticles.multiImageDetect(inimage,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,local_max=lm,output=True)
    return particle_data

def makeDetectionsAndMark(img,local_max=None):
    print('\n==== Start Localization and Detection ====')
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,local_max=local_max,output=False)

    if not dataCorrect(particle_data):
        sys.exit("Particle data not correct")

    return particle_data

#TODO: repair for new marking functions:
def makeDetectionFromFile():
    print("\n==== Series of all location pictures read from file ====")
    particle_data = convertFiles.readDetectedParticles("foundParticles.txt")
    pd = particle_data[:1]
    for i in xrange(len(pd)):
        image = readImage.readImage(img[i])
        markings = markPosition.markPositionsFromList(image.shape,particle_data[i])
        markPosition.superimpose(image,markings,"06mark-{:0004d}".format(i)+".png")
    return particle_data

def makeTracks(particle_data):
    print('\n==== Start Tracking ====')
    tracks = ctrack.link_particles(particle_data,max_displacement,min_track_len=0)
    return tracks

def readConfig(filename):
    global sigma 
    global local_max_window 
    global signal_power 
    global bit_depth 
    global eccentricity_thresh 
    global sigma_thresh 
    global max_displacement 
    global addUp
    global minTrackLen

    innumber = 10
    a = []
    infile = open(filename,'r')
    for i in xrange(2):
        infile.readline()
    counter = 0
    for line in infile:
        counter += 1
        if counter == 1 and line[0] != "#":
            counter -= 1
            continue
        if counter == 2 and line[0] == "#":
            counter -= 1
            continue
        elif counter == 2:
            counter = 0
            a.append(line.split()[0])
    #print a
    if len(a) < innumber:
        sys.exit("Input file missing {:} entries!".format(innumber-len(a)))
    elif len(a) > innumber:
        sys.exit("Input file has {:} too many entries!".format(len(a)-innumber))
    else:
        imagedir = a[0]
        sigma  = float(a[1])
        local_max_window  = float(a[8])
        signal_power  = float(a[2])
        bit_depth  = float(a[3])
        eccentricity_thresh  = float(a[7])
        sigma_thresh  = float(a[6])
        max_displacement  = float(a[4])
        addUp = int(a[5])
        minTrackLen = int(a[9])

    return imagedir

def compileMultiTracks(img,tr):
    print("Mark tracks in images")
    image = markPosition.autoScale(readImage.readImage(img[0]))
    posmark = np.zeros(image.shape)
    print('_'*52)
    count = 0
    sys.stdout.write("[")
    sys.stdout.flush()
    for i in xrange(len(img)):
        a = int(i * 50/len(img))
        if a > count:
            sys.stdout.write("#"*(a-count))
            sys.stdout.flush()
            count += a-count
        # read image i
        image = markPosition.autoScale(readImage.readImage(img[i]))
        data = markPosition.convertRGBGrey(image)
        mark = np.zeros(image.shape)
        for j in tr:
            # Make markings of track j for frame i and add to trackmarks
            # make markings for particle positions in frame i
            if not np.isnan(j.track[i]['x']):
                #print j.track[i]['frame'], i
                mark += markPosition.placeMarking(image.shape,j.track[i]['y'],j.track[i]['x'],markPosition.circle(radius=3))
                posmark += markPosition.connectPositions(image.shape,j.track[:i+1])
        # add trackmarks for frame i to image i
        data = markPosition.imposeWithColor(data,posmark,'B')
        # add particle position markings to image i
        data = markPosition.imposeWithColor(data,mark,'Y')
        # saveImage
        markPosition.saveRGBImage(data,"frame{:0004d}.tif".format(i+1))
    sys.stdout.write("#"*(50-a)+"]\n")
    return

def drawAllFoundTracks(img,tr):
    image = readImage.readImage(img[0])
    m = np.zeros(image.shape)
    if len(tr) == 0:
        return
    print('_'*52)
    count = 0
    sys.stdout.write("[")
    sys.stdout.flush()
    for t in xrange(len(tr)):
        a = int(t * 50/len(tr))
        if a > count:
            sys.stdout.write("#"*(a-count))
            sys.stdout.flush()
            count += a-count
        #print "doing track {:}".format(t)
        m += markPosition.connectPositions(image.shape,tr[t].track)
    markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"tr{:0004d}.tif".format(t))
    sys.stdout.write("#"*(50-a)+"]\n")
    return

#==============================
# Main
#==============================
def main():
    print("\n    ==================================\n"
            +"    = Welcome! Starting the Program. =\n"
            +"    ==================================\n")
    print("Switching path and copying setup file.")
    chPath("TesterNoKalman")

    # Read in setup file and sort
    img = readImageList(readConfig("setup.txt"))
    img = sorted(img)
    #img = img[:31]

    #print("Editing first image")
    #makeFirstImage(img)
    pd = makeDetectionsAndMark(img,"../SmallMito/Handmade Tracks/track02.txt")
    #print("Read particle data from file")
    #pd = convertFiles.readDetectedParticles("../Tses/foundParticles.txt")
    tr = makeTracks(pd)
    print("Done! Got all the data from images.\n"+ "-" * 52)
    
    print("\n==== Start Analysis ====")
    tr,liste = ctrack.readTrajectoriesFromFile("foundTracks.txt",minTrackLen)
    #TODO:Create images of positions
    compileMultiTracks(img,tr)
    print("Create images of single tracks")
    drawAllFoundTracks(img,tr)

    print("\nAppending trajectories to mega-trajectory")
    tra = analysisTools.appendTrajectories(tr,liste)
    print("\nCalculating MSD for comined Tracks")
    analysisTools.calcMSD(tra,"combined")

    return

if __name__=="__main__":
    main()

