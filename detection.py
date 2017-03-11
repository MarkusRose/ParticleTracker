
import Detection.detectParticles as dp
import Detection.readImage
import Detection.ctrack
import Detection.markPosition
import Detection.convertFiles
import Detection.analysisTools
import Detection.det_and_track

import numpy as np
import sys
from time import strftime



if __name__=="__main__":

    #System Parameters:
    #imagedir = "L:/Cel9A-6-9-10/45C/OD06/Experiment2/C-1"
    imagedir = "/media/markus/DataPartition/SimulationData/Images"
    bit_depth  = 16
    pathway = "C-1-AnalyzedData"
    #Detection Parameters:
    sigma  = 2
    local_max_window  = 10
    signal_power  = 1
    eccentricity_thresh = 4
    sigma_thresh  = 2
    addUp = 1 
    notCentroid = True

    print "Doing {:} to {:} now!".format(imagedir,pathway)

    #Change to Analysis folder
    Detection.det_and_track.chPath(imagedir+"/../"+pathway)


    #Read in image locations and names
    images = Detection.det_and_track.readImageList(imagedir)


    #Select for best signal_power from fifth image
    firstImage = Detection.readImage.readImage(images[5])
    #Detect in first image with different values of "signal_power" and save the images as files with detection markers
    signal_power_range = signal_power + 0.1*(np.arange(20)-10)
    count = 0
    for sig in signal_power_range:
        if sig <= 0:
            continue
        print("{:}. Testing for {:}.".format(count,sig))
        sys.stdout.flush()
        particles = dp.detectParticles(firstImage,sigma,local_max_window,sig,bit_depth,count,eccentricity_thresh,sigma_thresh,lmm=notCentroid)
        dp.outMarkedImages(firstImage,particles,"signal_check{:0004d}.tif".format(count))
        numparts = len(particles[0])
        print("    Found {:} particles.".format(numparts))
        sys.stdout.flush()
        if numparts == 0:
            break
        count += 1

    print("Which image is the best?")
    sys.stdout.flush()
    power_index = raw_input("Which image is the best?")
    power_index = float(power_index)
    if power_index != int(power_index) or power_index < 0 or power_index > len(signal_power_range):
        print("Index not valid. Quitting system now!")
        sys.stdout.flush()
        sys.exit(-1)
    
    
    particle_data = dp.multiImageDetect(images,sigma,local_max_window,signal_power_range[power_index],bit_depth,eccentricity_thresh,sigma_thresh,addUp,local_max=None,output=False,lmmethod=notCentroid,imageOutput=False)


    outfile = open("detection.log",'w')
    timestr = strftime("%Y-%m-%d %H:%M:%S")

    outfile.write("Detection Log File\n==================\n\n")
    outfile.write("Time:   {:}\n".format(timestr))
    outfile.write("\nSystem Parameters:\n------------------\n")
    outfile.write("Image Location:   {:}\n".format(imagedir))
    outfile.write("Bit depth:    {:}\n".format(bit_depth))
    outfile.write("Analysis Folder: {:}\n".format(pathway))
    outfile.write("\nDetection Parameters:\n---------------------\n")
    outfile.write("Signal Power = {:}\n".format(signal_power_range[power_index]))
    outfile.write("Sigma = {:}\n".format(sigma))
    outfile.write("Sigma-threshold = {:}\n".format(sigma_thresh))
    outfile.write("Eccentricity-threshold = {:}\n".format(eccentricity_thresh))
    outfile.write("Number of added Frames = {:}\n".format(addUp))
    outfile.write("Local Window Size (for filters) = {:}\n".format(local_max_window))
    outfile.write("Are Centroids Used?    {:}\n".format(not notCentroid))
    outfile.write(50*"-")


