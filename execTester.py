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

sigma = 1.0
local_max_window = 4
signal_power = 8
bit_depth = 16
eccentricity_thresh = 2
sigma_thresh = 3
max_displacement = 10
addUp = 1
minTrackLen = 1

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
        frame_count += 1
        for particle in frame:
            print particle.frame, addUp, frame_count
            if particle.frame != frame_count+addUp:
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
        markings = markPosition.markPositionsFromList(image.shape,[position])
        markedlines = markPosition.connectPositions(image.shape,tracks[numtrack-1].track[1:i+1])
        markPosition.justsuper(image,markings,markedlines,"marked"+str(i)+".tif")
        #markPosition.superimpose(image,markings,"marked"+str(i)+".tif")
        print ""

def makeFirstImage(img):
    print("\n==== Make first images ====")
    inimage = img[0:addUp]
    particle_data = detectParticles.multiImageDetect(inimage,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,True)
    return particle_data

def makeDetectionsAndMark(img):
    print('\n==== Start Localization and Detection ====')
    print("==== Series of all location pictures ====")
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,addUp,False)

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
    print('\n==== Start Tracking ====\n')
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
        minTrackLen = int(a[9])

    return imagedir

def compareInitNoInit(image,data,out):

    initPos = convertFiles.convImageJTrack(data)
    markInit = markPosition.markPositionsSimpleList(image.shape,initPos)
    
    partdata = detectParticles.giveInitialFitting(image,initPos,signal_power,sigma,sigma_thresh,eccentricity_thresh,bit_depth,"out.txt")
    markWithInit = markPosition.markPositionsFromList(image.shape,partdata)

    partdata = detectParticles.detectParticles(image,sigma,local_max_window,signal_power,bit_depth,0,eccentricity_thresh,sigma_thresh,True)
    markNoInit = markPosition.markPositionsFromList(image.shape,partdata[0])
    markFromNoInit = markPosition.markPositionsSimpleList(image.shape,readLocalMax("foundLocalMaxima.txt"))
    boxMarkings = markPosition.drawBox(image.shape,readBox("localBoxes.txt"))
    

    ofile = open("simNoInit.txt",'w')
    detectParticles.writeDetectedParticles(partdata,1,ofile)


    outar = markPosition.autoScale(markPosition.convertRGBGrey(image))
    #outar = markPosition.imposeWithColor(outar,markInit,'B')
    #outar = markPosition.imposeWithColor(outar,markFromNoInit,'G')
    outar = markPosition.imposeWithColor(outar,markNoInit,'R')
    outar = markPosition.imposeWithColor(outar,boxMarkings,'G')

    markPosition.saveRGBImage(outar,out)
    return


def lotsOfTrials():

    readConfig("setup.txt")

    image = readImage.readImage("simData.tif")
    signal_power = 14
    compareInitNoInit(image,"simResults.txt","simOut.tif")



    image = readImage.readImage("singleData1.tif")
    markPosition.saveRGBImage(markPosition.autoScale(image),"singleOData1scaled.tif")
    signal_power = 5
    compareInitNoInit(image,"singleResults1.txt","singleOut.tif")
    image += readImage.readImage("singleData2.tif")
    image += readImage.readImage("singleData3.tif")
    markPosition.saveRGBImage(markPosition.autoScale(image),"addedOData1scaled.tif")
    compareInitNoInit(image,"singleResults1.txt","addedOut.tif")



    #particle_data = makeDetectionFromFile()

    #makeTracks(particle_data)
    
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
    return
    
def chPath(path):

    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        option = raw_input("Careful! Path exists! Do you want to continue? [y,N] ")
        if not (option == "y" or option == "Y" or option == "Yes" or option == "yes" or option == "YES"):
            sys.exit("Data exists already. Quitting now.")
    print "copying new setup.txt"
    shutil.copyfile("setup.txt",path+"/setup.txt")
    os.chdir(path)

    return


def compileMultiTracks(img,tr):
    image = markPosition.autoScale(readImage.readImage(img[0]))
    posmark = np.zeros(image.shape)
    for i in xrange(len(img)-addUp):
        # read image i
        image = markPosition.autoScale(readImage.readImage(img[i]))
        data = markPosition.convertRGBGrey(image)
        mark = np.zeros(image.shape)
        for j in tr:
            # Make markings of track j for frame i and add to trackmarks
            # make markings for particle positions in frame i
            if not np.isnan(j.track[i]['x']):
                print j.track[i]['frame'], i
                mark += markPosition.placeMarking(image.shape,j.track[i]['y'],j.track[i]['x'],markPosition.circle(radius=3))
                posmark += markPosition.connectPositions(image.shape,j.track[:i+1])
        # add trackmarks for frame i to image i
        data = markPosition.imposeWithColor(data,posmark,'B')
        # add particle position markings to image i
        data = markPosition.imposeWithColor(data,mark,'Y')
        # saveImage
        markPosition.saveRGBImage(data,"frame{:0004d}.tif".format(i))
    return


def main():
    chPath("./Tses")

    img = readImageList(readConfig("setup.txt"))
    img = sorted(img)
    for i in img:
        print i

    #makeFirstImage(img)
    pd = makeDetectionsAndMark(img)
    #pd = convertFiles.readDetectedParticles("../Tses/foundParticles.txt")
    tr = makeTracks(pd)

    image = readImage.readImage(img[0])
    m = markPosition.connectPositions(image.shape,tr[0].track)
    markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"tester.tif")

    print("Reading Tracks again, making pictures and imaging.")

    tr,liste = ctrack.readTrajectoriesFromFile("foundTracks.txt",minTrackLen)
    m = np.zeros(image.shape)
    for t in liste:
        print "doing track {:}".format(t)
        m += markPosition.connectPositions(image.shape,tr[t-1].track)
    markPosition.saveRGBImage(markPosition.convertRGBMonochrome(m,'B'),"tr{:0004d}.tif".format(t))
    print("\nAppending trajectories to mega-trajectory")
    tra = analysisTools.appendTrajectories(tr,liste)

    print("\nCalculating MSD for comined Tracks")
    analysisTools.calcMSD(tra,"combined")

    return

if __name__=="__main__":
    #img = readImageList(readConfig("setup.txt"))
    #img = img[:1]
    #for i in img:
    #    print i
    #makeFirstImage(img)
    main()

    #os.chdir("./Nehad06")
    #tr,liste = ctrack.readTrajectoriesFromFile("foundTracks.txt")
    #tra = analysisTools.appendTrajectories(tr,liste)
    #analysisTools.calcMSD(tra,"combined")

