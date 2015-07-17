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

sV = Fileio.getSysProps()
D = np.array([sV[0],sV[1],sV[2]])
p = np.array([[0,sV[3],sV[5]],[sV[4],0,sV[6]],[sV[7],sV[8],0]])
frames = int(sV[9])
N = int(sV[10])
tau = sV[11]
numPixels = int(sV[12])
wavelength = sV[13]
pixel_size = sV[14]
numAperture = sV[15]
mag = sV[16]
sigToNoise = sV[17]
intensity = sV[18]

statProbs = []
sumprobs = sV[3]+sV[4]+sV[5]+sV[6]+sV[7]+sV[8]
statProbs.append((sV[4]+sV[7])/sumprobs)
statProbs.append((sV[3]+sV[8])/sumprobs)
statProbs.append((sV[5]+sV[6])/sumprobs)

atracks = []

for n in xrange(N):
    track = []
    for i in xrange(0,frames,1):
        particle = np.zeros((11))
        particle[0] = i
        if len(track)  == 0:
            particle[3] = 0
            particle[4] = 0
            u = random.random()
            if u < statProbs[2]:
                particle[5] = 2
            elif u < (statProbs[2] + statProbs[1]):
                particle[5] = 1
            else:
                particle[5] = 0
        else:
            particle[3] = track[-1][3] + track[-1][1]
            particle[4] = track[-1][4] + track[-1][2]
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
        particle[1] = random.gauss(0,2*D[particle[5]]*tau)
        particle[2] = random.gauss(0,2*D[particle[5]]*tau)
        for k in xrange(6,10,1):
            particle[k] = 0
        particle[10] = n
        track.append(particle)
    atracks.append(track)
print atracks
    
Fileio.setTrackFile(atracks)
