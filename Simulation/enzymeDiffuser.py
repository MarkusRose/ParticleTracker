import numpy as np
import random
import Fileio

'''
This program creates multiple tracks of gaussian random walks. 

The input parameters are:
(D1, D2, D3, p12, p21, p13, p23, p31, p32,
 number of frame, number of particles, acquisition time, pixel array,
 wavelength, Pixel size, NA, magnification, S/N, Intensity)

The output parameters are:
All Tracks = [Track1,Track2,Track3,...]
Tracki = [Particle1, Particle2, ...]
Particle1 = [frame, dx, dy, x, y, state, Intensity, 
 Background, sigma_x, sigma_y, Particle ID]
'''

#Read in Values from file
sV = Fileio.getSysProps()
#Diff constants of 3 states
D = np.array([sV[1],sV[2],sV[3]]) 
#Markov probability matrix for state switching
p = np.array([[0,sV[4],sV[6]],[sV[5],0,sV[7]],[sV[8],sV[9],0]]) 
#Number of frames
frames = int(sV[10])
#Number of particles
N = int(sV[11])
#Acquisition time
tau = sV[12]
#Number of pixels (side of square)
numPixels = int(sV[13])
#Other properties
wavelength = sV[14]
pixel_size = sV[15]
numAperture = sV[16]
mag = sV[17]
sigToNoise = sV[18]
intensity = sV[19]

#Initial probabilities for choosing state
'''
pi1 = ( p21 + p31 ) / (p12 + p13 + p21 + p23 + p31 + p32)
pi2 = ( p12 + p32 ) / (p12 + p13 + p21 + p23 + p31 + p32)
pi3 = ( p13 + p23 ) / (p12 + p13 + p21 + p23 + p31 + p32)
'''
statProbs = []
sumprobs = sV[4]+sV[5]+sV[6]+sV[7]+sV[8]+sV[9]
statProbs.append((sV[5]+sV[8])/sumprobs)
statProbs.append((sV[4]+sV[9])/sumprobs)
statProbs.append((sV[6]+sV[7])/sumprobs)

#output variable
atracks = []
for n in xrange(N):
    #one individual track
    track = []

    for i in xrange(0,frames,1):

        #particle in one frame
        particle = np.zeros((11))

        #frame number
        particle[0] = i

        #first or not?
        if len(track)  == 0:
            #initial position
            particle[3] = 0
            particle[4] = 0

            #choose state
            u = random.random()
            if u < statProbs[2]:
                particle[5] = 2
            elif u < (statProbs[2] + statProbs[1]):
                particle[5] = 1
            else:
                particle[5] = 0

        else:

            #Calc new absolut position
            particle[3] = track[-1][3] + track[-1][1]
            particle[4] = track[-1][4] + track[-1][2]

            #choose new state
            u = random.random()
            s0 = track[-1][5]
            s1 = (s0+1) % 3
            s2 = (s0+2) % 3
            if u < p[s0,s2]:
                particle[5] = s2
            elif u < (p[s0,s2] + p[s0,s1]):
                particle[5] = s1
            else:
                particle[5] = s0

        #Generate displacement in correct state
        particle[1] = random.gauss(0,2*D[particle[5]]*tau)
        particle[2] = random.gauss(0,2*D[particle[5]]*tau)

        #Rest of particle variables
        for k in xrange(6,10,1):
            particle[k] = 0

        particle[10] = n

        #Append particle to track
        track.append(particle)

    #Append Track to output var
    atracks.append(track)

#Print tracks to file
Fileio.setTrackFile(atracks)
