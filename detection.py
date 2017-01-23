
import Detection.detectParticles as dp
import Detection.readImage
import Detection.ctrack
import Detection.markPosition
import Detection.convertFiles
import Detection.analysisTools
import Detection.det_and_track

import numpy as np
import sys


if __name__=="__main__":

    imagedir = "C:/Users/Markus/Desktop/C-1"
    sigma  = 2
    local_max_window  = 10
    signal_power  = 1.5
    bit_depth  = 16
    eccentricity_thresh  = 4
    sigma_thresh  = 2
    addUp = 1 
    notCentroid = True
    pathway = "AnalyzedData"
    Detection.det_and_track.chPath(imagedir+"/../"+pathway)
    notCentroid = True

    

    #Read in image locations and names
    images = Detection.det_and_track.readImageList(imagedir)

    #Select for best signal_power
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

    
    power_index = raw_input("Which image is the best?")
    power_index = float(power_index)
    if power_index != int(power_index) or power_index < 0 or power_index > len(signal_power_range):
        print("Index not valid. Quitting system now!")
        sys.stdout.flush()
        sys.exit(-1)
    
    
    particle_data = Detection.detectParticles.multiImageDetect(images,sigma,local_max_window,signal_power_range[power_index],bit_depth,eccentricity_thresh,sigma_thresh,addUp,local_max=None,output=False,lmmethod=notCentroid,imageOutput=True)


