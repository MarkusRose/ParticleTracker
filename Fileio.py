#==================================
#===   File in-/output
#==================================

'''
This script reads and generates the 4 used filetypes in this
program. It contains getter and setter functions for each type.
'''

#System Properties
#-----------------
#The input parameters have to be of the shape:
'''
(D1, D2, D3, p12, p21, p13, p23, p31, p32,
 number of frame, number of particles, acquisition time, pixel array,
 wavelength, Pixel size, NA, magnification, S/N, Intensity)
'''
#setter
def setSysProps(paramArray):
    outfile = open("SystemParameters.txt",'w')
    outfile.write("#System Parameteres for [Program]\n")
    outfile.write("#\n")

    outfile.write("#Diffusion constants [D1, D2, D3] (um^2/s)\n")
    for i in xrange(0,3,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Transition probabilities [p12, p21, p13, p23, p31, p32]\n")
    for i in xrange(3,9,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Imaging properties [numFrames, numParticles, tau (ms), numPixels-1d]\n")
    for i in xrange(9,13,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Camera Properties [lambda (nm), pixel size (um)]\n")
    for i in xrange(13,15,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#Microscope Properties [NA, magnification, S/N, Intensity (#photons)\n")
    for i in xrange(15,19,1):
        outfile.write(str(paramArray[i])+" ")
    outfile.write("\n\n#EOF\n")
    
    outfile.close()
    return
    


#getter
def getSysProps():
    pA = []
    infile = open("SystemParameters.txt",'r')
    for line in infile:
        if len(line) == 0 or line[0] == "#":
            continue
        else:
            k = line.split()
            for i in k:
                pA.append(float(i))
    return pA

#Frame-by-frame Detection
#------------------------
#The input parameters have to be of the shape:
'''
All Frames = [Frame1,Frame2,Frame3,...]
Framei = [Particle1, Particle2, ...]
Particle1 = [frame, x, y, delta_x, delta_y, Intensity, 
 Background, sigma_x, sigma_y, Particle ID]
So: All Frames = [[[],[],...],[[],[],...],....]
'''
#setter
def setDetection(detParts):
    outfile = open("DetectedParticles.txt",'w')
    outfile.write("#Frame-by-frame list of detected particles\n")

    for frame in xrange(len(detParts)):
        outfile.write("\n")
        outfile.write("#Frame "+str(frame+1)+":\n")
        outfile.write("#Frame  X_pos  Y_pos  X_err  Y_err  Intensity  Background  sigma_X  sigma_Y  ParticleID\n")
        for particle in detParts[frame]:
            for prop in particle:
                outfile.write(str(prop) + " ")
            outfile.write("\n")
        outfile.write("\n")

    outfile.close()                        
    return

#getter
def getDetection():
    ffdets = []
    frame = []
    particle = []
    infile = open("DetectedParticles.txt",'r')
    openTrack = 0
    for line in infile:
        if line[0] == '#':
            continue
        elif line[0] == "\n":
            if openTrack == 0:
                openTrack = 1
            else:
                ffdets.append(frame)
                frame = []
                openTrack = 0
        else:
            for elem in line.split():
                particle.append(float(elem))
            frame.append(particle)
            particle = []
                
    return ffdets

#Individual Tracks
#-----------------
#The input parameters have to be of the shape:
'''
All Tracks = [Track1,Track2,Track3,...]
Tracki = [Particle1, Particle2, ...]
Particle1 = [frame, dx, dy, x, y, state, Intensity, 
 Background, sigma_x, sigma_y, Particle ID]
'''
#setter
def setTrackFile(detTracks):
    outfile = open("Tracks.txt",'w')
    outfile.write("#All found tracks\n")

    for track in xrange(len(detTracks)):
        outfile.write("\n")
        outfile.write("#Track "+str(track+1)+":\n")
        outfile.write("#Frame  dX  dY  X_pos  Y_pos  State  Intensity  Background  sigma_X  sigma_Y  ParticleID\n")
        for particle in detTracks[track]:
            for prop in particle:
                outfile.write(str(prop) + " ")
            outfile.write("\n")
        outfile.write("\n")

    outfile.close()                        
    return

#getter
def getTrackFile():
    alltracks = []
    track = []
    particle = []
    infile = open("Tracks.txt",'r')
    openTrack = 0
    for line in infile:
        if line[0] == '#':
            continue
        elif line[0] == "\n":
            if openTrack == 0:
                openTrack = 1
            else:
                alltracks.append(track)
                track = []
                openTrack = 0
        else:
            for elem in line.split():
                particle.append(float(elem))
            track.append(particle)
            particle = []
                
    return alltracks


#Read and write tiff Images
#--------------------------
#setter
def setImages():
    pass

#getter
def getImages():
    pass
    

#So this is what there is to be done
'''
still need the images
the rest works
'''
