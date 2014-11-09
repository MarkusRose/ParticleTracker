import detectParticles
import readImage
import ctrack
import sys
import markPosition
import pysm
import os
import glob
import convertFiles
from scipy import ndimage
from matplotlib import pyplot as plt

import numpy as np

sigma = 1.0
local_max_window = 4
signal_power = 8
bit_depth = 16
eccentricity_thresh = 2
sigma_thresh = 3
max_displacement = 6
addUp = 3

def readImageList(path):
    print path
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
        frame_count += addUp
        for particle in frame:
            if particle.frame != frame_count:
                output = False
                print ("nope, particle aint in right frame.")
                break
        if not output:
            break
    return output 
        

def testTracks(tracks):        
    print("Done creating tracks")
    print('ChooChoo! Track 29: \n' + str(tracks[29].track))
    print("Boy, you can give me a schein")
    for name in tracks[29].track.dtype.names:
        print(name + ": " + str(tracks[29].track[name]))
    return   

def printPictures(tracks,numtrack):
    position = pysm.new_cython.TempParticle()
    for i in xrange(1,40):
        print("# {:} =====================".format(i))
        image = readImage.readImage(img[i-1])
        position.x= tracks[numtrack-1].track[i]['x']
        position.y= tracks[numtrack-1].track[i]['y']
        markings = markPosition.markPositionsFromList(image,[position])
        markedlines = markPosition.connectPositions(image,tracks[numtrack-1].track[1:i+1])
        markPosition.justsuper(image,markings,markedlines,"marked"+str(i)+".tif")
        #markPosition.superimpose(image,markings,"marked"+str(i)+".tif")
        print ""

def makeFirstImage(img):
    print("\n==== Make first images ====")
    inimage = img[0:addUp]
    particle_data = detectParticles.multiImageDetect(inimage,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,True)
    image = readImage.readImage(inimage[0])
    markings = markPosition.markPositionsFromList(image,particle_data[0])
    markPosition.superimpose(image,markings,"06mark.tif")
    return particle_data

def makeDetectionsAndMark(img):
    print('\n==== Start Localization and Detection ====')
    print("==== Series of all location pictures ====")
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,False)

    if not dataCorrect(particle_data):
        sys.exit("Particle data not correct")

    for i in xrange(len(img)/addUp):
        image = readImage.readImage(img[i*addUp])
        markings = markPosition.markPositionsFromList(image,particle_data[i])
        markPosition.superimpose(image,markings,"06mark-{:0004d}".format(i)+".png")
    return particle_data

def makeDetectionFromFile():
    print("\n==== Series of all location pictures read from file ====")
    particle_data = convertFiles.readDetectedParticles("foundParticles.txt")
    pd = particle_data[:1]
    for i in xrange(len(pd)):
        image = readImage.readImage(img[i])
        markings = markPosition.markPositionsFromList(image,particle_data[i])
        markPosition.superimpose(image,markings,"06mark-{:0004d}".format(i)+".png")
    return particle_data

def makeTracks(particle_data):
    print('\n==== Start Tracking ====\n')
    tracks = ctrack.link_particles(particle_data,max_displacement,min_track_len=0)
    return

def readConfig(filename):
    global sigma 
    global local_max_window 
    global signal_power 
    global bit_depth 
    global eccentricity_thresh 
    global sigma_thresh 
    global max_displacement 
    global addUp

    innumber = 9

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
        if counter == 2:
            counter = 0
            a.append(line.split()[0])

    print a

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

    return imagedir


if __name__=="__main__":
    

    img = readImageList(readConfig("setup.txt"))
    
    img = img[51:88]


    '''
    image = readImage.readImage(img[0])
    addedImages = []
    a = np.zeros(image.shape)
    numImg = 3
    for i in xrange(len(img)):
        image = readImage.readImage(img[i])
        a += image
        if (i+1) % numImg == 0:
            readImage.saveImageToFile(a,"AddedImages/addedImg{:0004}.tif".format((i+1)/3))
            a = np.zeros(image.shape)

    
    img = readImageList("AddedImages")
    '''

    #makeFirstImage(img)

    #particle_data = makeDetectionsAndMark(img)

    particle_data = makeDetectionFromFile()

    makeTracks(particle_data)
    
    #tracks = convertFiles.convImageJTrack("/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/VisTrack01.xls")

    '''
    image = readImage.readImage(img[tracks[0][0]-1])
    print(tracks[0][0])
    print(tracks[0][1],tracks[0][2])
    print(image[tracks[0][1],tracks[0][2]])
    '''
    #oname = "/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/newTrack02.txt"
    #detectParticles.giveInitialFitting(img,tracks,signal_power,sigma,sigma_thresh,eccentricity_thresh,bit_depth,oname)
    
    print("\nDone!\n---------\n")
