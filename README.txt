'''==============================
=== Markus Rose               ===
=============================='''



README file for Particle-Searcher
=================================

Packages
========

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

