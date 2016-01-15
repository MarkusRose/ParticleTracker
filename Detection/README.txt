'''==============================
=== Markus Rose               ===
=============================='''



README file for Particle-Searcher
=================================

Packages
========

ctrack
------
class ParticleTrack(object):
-writeTrajectories(tracks):
-link_particles(particle_data, max_displacement,
-build_cost_matrix(
-particles_1,
-particles_2,
-max_cost,
-cost_matrix):
-lap_assoc_matrix(
-    max_cost,
-    association_matrix, 
-    cost_matrix):

detectParticles
---------------
-writeDetectedParticles(particles):
-multiImageDetect(img,
                sigma,
                local_max_window,
                signal_power,
                bit_depth,
                eccentricity_thresh,
                sigma_thresh,output=False):
-fitgaussian2d(data, background_mean, user_moments = None):
-image_moments(data, mean_background):
-gaussian2d(height, amplitude, center_x, 
-detectParticles(img,sigma,local_max_window,signal_power,
                bit_depth,frame,eccentricity_thresh,sigma_thresh,output):

readImage
---------
-readImage(imagepath)
-adjustRange(image,bit_depth)
-determineCutoff(image)
-otsuMethod(image)
-cutImage(image,cutoffMethod)
-saveImageToFile(inArray,outName)
-detectParticlePosition(inImage,outImage,cutoffMethod)

markPosition
------------
-treasure(size_x,size_y,thickness)
-placeWidget(image,pos_x,pos_y)
-drawLine(one_x,one_y,two_x,two_y)
-placeImage(bild,img,x,y)
-placeLine(image,one_x,one_y,two_x,two_y)
-markPositionsFromList(image,posList)
-connectPositions(image,posList)
-convertRGB(image)
-imposeColor(data,mark,color='R')
-saveRGBImage(data,name)
-superconnected(image,markings,name)
-justsuper(image,markings,markedlines,name)
-superimpose(image,markings,name)
-makeRegularImage()


filters
-------
-boxcarFilter(image,boxsize=3,cutoff=1.0)
    image: nd.array of the image
    boxsize: size of box overwhich to average
    cutoff: cutoff for intensity
    return: filtered image as nd.array

convertFiles
------------
- readTrajectoryFromFile(filename)
    filename: name of trajectory file
    return: track = list of (frame, x, y)
- readPositionsFromFile(filename)
    filename: name of Position file
    return: pos = list of (frame, x, y, width_x, width_y, height, amplitude,
        SNR, Volume)
- sortPositionFile(filename)
    Saves sorted positions from file <filename> to file <filename>
    filename: position file name
    return: void
- convertParticles(infile)
    infile: input file name
    return: void
- convertTrajectories(infile)
    infile: input file name
    return: void

analysisTools
-------------
- calcMSD(track):
    Reads a track as a list and calculates the MeanSquareDisplacement.
    Prints MSD as framenumber vs msd to file "msd<fileident>.txt"
    track: list of track points p[1] = xpos, p[2] = ypos
    fileident(optional): adds identifyer to filename
    return: void 

