import detectParticles
import readImage
import ctrack
import sys
import markPosition
import pysm
import os
import glob
import convertFiles
from matplotlib import pyplot as plt

import numpy as np

sigma = 1.0
local_max_window = 3
signal_power = 6
bit_depth = 16
eccentricity_thresh = 1.5
sigma_thresh = 3
max_displacement = 6

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



if __name__=="__main__":

    img = readImageList("/data/NEHADexperiments/2013-08-14/mito_DID006_Images")


    img = img[:10]

    '''
    print("\n==== Make first images ====")
    inimage = img[0]
    particle_data = detectParticles.multiImageDetect([inimage],sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,True)
    image = readImage.readImage(inimage)
    markings = markPosition.markPositionsFromList(image,particle_data[0])
    markPosition.superimpose(image,markings,"06mark.tif")
    '''

    print('\n==== Start Localization and Detection ====')
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,False)

    if not dataCorrect(particle_data):
        sys.exit("Particle data not correct")

    print("\n==== Series of all location pictures ====")
    for i in xrange(len(img)):
        image = readImage.readImage(img[i])
        markings = markPosition.markPositionsFromList(image,particle_data[i])
        markPosition.superimpose(image,markings,"06mark-"+str(i)+".tif")
   
    '''
    print('\n==== Start Tracking ====\n')
    tracks = ctrack.link_particles(particle_data,max_displacement)
    '''
    

    print("\nDone!\n---------\n")
