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



class detectAndTrack():
    def __init__(self):
        #==============================
        # Global Variables
        #==============================
        self.imagedir = ""
        self.sigma = 1.0
        self.local_max_window = 4
        self.signal_power = 8
        self.bit_depth = 16
        self.eccentricity_thresh = 2
        self.sigma_thresh = 3
        self.max_displacement = 10
        self.addUp = 1
        self.minTrackLen = 1
        self.bFLAG = False
        self.lm = None
        self.pathway = "AnalyzedData"
        self.notCentroid = False

        

    def runDetectionAndTracking(self):
        # Read in setup file and sort
        innum = 13
        self.readConfig("setup.txt",innum)
        self.img = readImageList(self.imagedir)
        self.img = sorted(self.img)
        #self.img = self.img[:10]
        self.particles = self.makeDetectionsAndMark()
        self.tracks = self.makeTracks()
        print len(self.tracks)

    def runDetection(self):
        # Read in setup file and sort
        innum = 13
        self.readConfig("setup.txt",innum)
        self.img = readImageList(self.imagedir)
        self.img = sorted(self.img)
        #self.img = self.img[:10]
        self.particles = self.makeDetectionsAndMark()

    def runTracking(self):
        # Read in setup file and sort
        innum = 12
        self.readConfig("setupTracking.txt",innum)
        #self.img = readImageList(self.imagedir)
        #self.img = sorted(self.img)
        print "Got to here"
        self.particles = convertFiles.readDetectedParticles(self.lm)
        self.tracks = self.makeTracks()
        print len(self.tracks)

    def readConfig(self,filename,innumber):
        
        a = []
        infile = open(filename,'r')
        counter = 0
        for line in infile:
            counter += 1
            if counter in xrange(5,43,3):
                a.append(line.split()[0])
                continue
        if len(a) < innumber:
            sys.exit("Input file missing {:} entries!".format(innumber-len(a)))
        elif len(a) > innumber+1:
            sys.exit("Input file has {:} too many entries!".format(len(a)-innumber))
        else:
            self.imagedir = a[0]
            self.sigma  = float(a[1])
            self.local_max_window  = float(a[8])
            self.signal_power  = float(a[2])
            self.bit_depth  = float(a[3])
            self.eccentricity_thresh  = float(a[7])
            self.sigma_thresh  = float(a[6])
            self.max_displacement  = float(a[4])
            self.addUp = int(a[5])
            self.minTrackLen = int(a[9])
            self.pathway = a[11]
            self.lm = a[10]
            if innumber == 13:
                self.notCentroid = (a[12] == "1")
            if self.lm == "#":
                self.lm = None
        if self.lm != None:
            chPath(os.path.dirname(self.lm))
        else:
            if self.imagedir != "Please select Folder containing Images":
                chPath(self.imagedir+"/../"+self.pathway)
            else:
                print "Didn't Work, please restart!"
                sys.exit(1)
        return
        
    def makeDetectionsAndMark(self):
        particle_data = detectParticles.multiImageDetect(self.img,self.sigma,self.local_max_window,self.signal_power,self.bit_depth,self.eccentricity_thresh,self.sigma_thresh,self.addUp,local_max=self.lm,output=False,lmmethod=self.notCentroid)

        if not dataCorrect(particle_data,self.addUp):
            sys.exit("Particle data not correct")

        return particle_data


    def makeTracks(self):
        tracks = ctrack.link_particles(self.particles,self.max_displacement,self.minTrackLen)
        return tracks




#==============================
# General Functions
#==============================
def chPath(path):

    if not os.path.isdir(path):
        os.mkdir(path)
    try:
        shutil.copyfile("setup.txt",path+"/setup.txt")
        shutil.copyfile("setupTracking.txt",path+"/setupTracking.txt")
    except:
        print "Setup couldn't be copied. It is the same File!"
    os.chdir(path)

    return

def readImageList(path):
    if not os.path.isdir(path):
        print "No path named " + path
        raise ValueError, "No path named " + path
    img = glob.glob(os.path.join(path, '*.tif'))
    print "Number of images found: " + str(len(img))
    return img

def dataCorrect(particle_data,addUp):
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
    print("\nEditing first image")
    if len(img) > 2*addUp:
        l = int(len(img)/2)
        inimage = img[l:addUp+l]
    elif len(img) >= addUp:
        inimage = img[0:addUp]
    else:
        raise Exception("Not enough images given to perform make first visual.")
    particle_data = detectParticles.multiImageDetect(inimage,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,local_max=lm,output=True)
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

def makeTracks(self,particle_data):
    tracks = ctrack.link_particles(particle_data,max_displacement,min_track_len=0)
    return tracks


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
def leftovers():
    print("\n    ==================================\n"
            +"    = Welcome! Starting the Program. =\n"
            +"    ==================================\n")
    '''
    print("Switching path and copying setup file.")

    print("\nPlease select a folder: \n")
    pathway = raw_input()
    chPath(pathway)
    '''

    # Read in setup file and sort
    img = readImageList(readConfig("setup.txt"))
    img = sorted(img)
    img = img[:10]
    
    print("{:} images selected for analysis.".format(len(img)))
    
    firstImageFLAG = False
    if firstImageFLAG:
        makeFirstImage(img)
        print("Done! See first image at " + pathway + ".")
        return

    print('\n==== Start Localization and Detection ====')
    detectFLAG = True
    if detectFLAG:
        pd = makeDetectionsAndMark(img,lm)
    else:
        print("Read particle data from file")
        pd = convertFiles.readDetectedParticles("../Tses/foundParticles.txt")
    print("Done Localization and Detection\n")
    """
    print('\n==== Start Tracking ====')
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
    """

    return


if __name__=="__main__":
    run = detectAndTrack()
    

