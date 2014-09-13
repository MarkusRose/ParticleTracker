import detectParticles
import readImage
import ctrack
import sys
import markPosition
import pysm

import numpy as np

img = [
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image1.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image2.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image3.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image4.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image5.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image6.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image7.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image8.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image9.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image10.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image11.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image12.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image13.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image14.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image15.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image16.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image17.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image18.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image19.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image20.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image21.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image22.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image23.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image24.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image25.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image26.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image27.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image28.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image29.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image30.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image31.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image32.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image33.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image34.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image35.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image36.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image37.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image38.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image39.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image40.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image41.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image42.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image43.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image44.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image45.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image46.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image47.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image48.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/10PDiff/mol_image49.tif"
    ]
sigma = 1.0
local_max_window = 3
signal_power = 14
bit_depth = 16
eccentricity_thresh = 1.5
sigma_thresh = 3
max_displacement = 50

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


    print("\n==== Series of all location pictures ====")
    for i in xrange(len(img)):
        inimage = img[i]
        particle_data = detectParticles.multiImageDetect([inimage],sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,False)

        image = readImage.readImage(inimage)
        markings = markPosition.markPositionsFromList(image,particle_data[0])
        markPosition.superimpose(image,markings,"06mark-"+str(i)+".tif")
   
    print("\n==== Make first images ====")
    inimage = img[26]
    particle_data = detectParticles.multiImageDetect([inimage],sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,True)

    image = readImage.readImage(inimage)
    markings = markPosition.markPositionsFromList(image,particle_data[0])
    markPosition.superimpose(image,markings,"06mark.tif")

    print('\n==== Start Localization and Detection ====')
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh,False)

    if not dataCorrect(particle_data):
        sys.exit("Particle data not correct")

    print('\n==== Start Tracking ====\n')
    tracks = ctrack.link_particles(particle_data,max_displacement)
    
    printPictures(tracks,4)

    print("\nDone!\n---------\n")
