#!/usr/bin/env python

'''
Hidden Markov model analysis of 2D single particle tracks
Ref: Das et al, PLoS Comp Biol (2009)

Created by: Raibatak Das
Date: Oct 2015
'''

import numpy as np
from math import exp, log
import csv
import random
import sys

# Function definitions

def importTracks(filename):
    '''Import tracks from csv file'''
    with open(filename) as f:
        csvdata = csv.reader(f)
        next(csvdata, None) # skip header
        return np.array( [map(float, row) for row in csvdata] )

#read in Tracks
def readTracks(infile):
    fopen = open(infile,'r')

    tracks = []
    track = []
    brt = False

    for line in fopen:

        if len(line.strip()) == 0:
            if brt:
                brt = False
                if len(track) != 0:
                    tracks.append(np.array(track))
                del track
                track = []
            continue
        elif line[0] == '#':
            if not brt:
                brt = True
                track = []
            continue
        track.append(np.array(map(float,line.split())))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    return np.array(tracks)


def sqdis(tracks):
  '''
  Compute squared displacement for all tracks
  '''
  # Extract particle IDs
  particleIDs = np.unique(tracks[:,-1])
  rsquared = []
  # Compute squared displacements
  for particle in particleIDs:
    dr = tracks[tracks[:,-1] == particle][:, [1,2]]
    dr2 = np.sum(dr**2, axis=1)
    rsquared.append(dr2)
  return rsquared

def logsum(a, b): 
  '''
  logsum(a, b) = log(exp(a) + exp(b))
  '''
  return a + log(1+exp(b-a)) if a>b else b + log(1+exp(a-b))

def loglikelihood(theta, rsquared, tau):
  '''
  log likelihood of parameters for a 2-state hidden Markov model

  theta -- HMM parameters [log10(D1), log10(D2), p12, p21]
  rsquared -- observed sequence of squared displacements
  tau -- time interval between frames (tau = 1/frame rate)
  '''
  # Extract parameters
  D1, D2 = 10**theta[0], 10**theta[1]
  p12, p21 = theta[2], theta[3]
  nsteps = np.size(rsquared, 0)
  logstatprob = np.log([p21/(p21 + p21), p12/(p12 + p21)])
  logtransprob = np.log([[1 - p12, p12], [p21, 1-p21]])
  # Compute single step log likelihoods (eq 19 - Das et al)
  loglike = np.array( [[-rsq/(4*D*tau) for D in [D1, D2]] for rsq in rsquared] ) - [log(D1*tau), log(D2*tau)]
  # Compute forward variable alpha (algorithm 2 - Das et al)
  logalpha = np.empty_like(loglike)
  logalpha[0,:] = logstatprob + loglike[0,:]
  for j in xrange(1, nsteps):
    logalpha[j,:] = map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:]) + loglike[j, :]
  return logsum(logalpha[-1,0], logalpha[-1, 1])

# Usage
def doMetropolis2(allTracks):

    print len(allTracks)
    
    # Select a track by particle ID (the last column) and extract particle positions
    particleID = 0
    dr = allTracks[:, [1,2]]
    
    # Compute squared displacements for selected track
    dr2 = np.sum(dr**2, axis=1)

    #dr2 = sqdis(allTracks)


    dt = 0.1
    N = 100
    theta = []
    L = []
    vartheta = np.array([4,4,0.2,0.2])
    theta.append(np.array([10,-5,0.1,0.1]))
    proptheta = theta[-1][:]

    ll = loglikelihood(proptheta, dr2, dt)
    L.append(ll)

    #llcombined = map(lambda track: loglikelihood(proptheta, track, dt), dr2)
    #L.append(sum(llcombined))
    
    outfile = open("hiddenMCMC2.txt",'w')
    outfile.write("#Hidden Markov Chain Monte Carlo\n")
    outfile.write("# LogLikelyhood   x   y\n")
    outfile.write(str(L[-1]) + ' ' + str(theta[-1][0]) + ' ' + str(theta[-1][1]) + '\n')
    outpropsf = open("proposedHMM.txt",'w')
    outpropsf.write("# LogLikelyhood   x   y\n")

    breakout = False
    
    i = 0
    while True:
        Lmax = L[-1]
        index = 0
        props = []
        props.append([Lmax, theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]])
        j = 0
        C = 1000
        #for j in xrange(100):
        while j < 100 or Lmax <= L[-1]:
            dtheta = np.zeros((4))
            #proptheta = theta[-1]
            for l in xrange(4):
                if l in [2,3]:
                    while dtheta[l] == 0. or (theta[-1][l] + dtheta[l] < 0 or theta[-1][l] + dtheta[l] > 1):
                        dtheta[l] = random.gauss(0,vartheta[l])
                else:
                    dtheta[l] = random.gauss(0,vartheta[l])
            #print dtheta
            proptheta = theta[-1] + dtheta
            ll = loglikelihood(proptheta, dr2, dt)
            Ltest = ll
            
            #llcombined = map(lambda track: loglikelihood(proptheta, track, dt), dr2)
            #Ltest = sum(llcombined)
        
            props.append([Ltest, proptheta[0], proptheta[1], proptheta[2], proptheta[3]])
            for l in xrange(len(props[-1])):
                outpropsf.write(str(props[-1][l])+' ')
            outpropsf.write("\n")
            if Lmax < Ltest:
                Lmax = Ltest
                index = j+1
            j+=1
            if j > 10000:
                breakout = True
                break
        print j
        outpropsf.write("\n\n")
        theta.append(np.array([props[index][1],props[index][2],props[index][3],props[index][4]]))
        L.append(props[index][0])
        print i
        i += 1
        C += 1000
        outfile.write(str(L[-1]))
        for k in xrange(2):
            outfile.write(' ' + str(theta[-1][k]))
        outfile.write('\n')
        print L[-1], 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
        if breakout:
            for l in xrange(len(vartheta)):
                if l in [2,3]:
                    vartheta[l] /= 2.0
                else:
                    vartheta[l] /= 2.0
            print "TRUE", vartheta
            breakout = False
        if vartheta[0] < 0.001:
            break
    outfile.close()
    print "RESULTS:"
    print Lmax, theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]
    return theta, L

if __name__=="__main__":
    # Import all tracks
    #allTracks = importTracks('foundTracks.csv')
    allTracks2 = np.array(readTracks('combinedTrack-relativeXYDisplacements.txt'))
    sha = allTracks2.shape
    allTracks = allTracks2.reshape(sha[0]*sha[1],sha[2])
    print allTracks.shape
    #sys.exit(0)
    # Select a track by particle ID (the last column) and extract particle positions
    particleID = 0
    dr = allTracks[allTracks[:,-1] == particleID][:, [1,2]]
     
    # Compute squared displacements for selected track
    dr2 = np.sum(dr**2, axis=1)
     
    # Compute log likelihood for some parameter guess and selected track
    dt = 0.1 # dt = 1/frame rate
    thetaguess = [-2, 1, 0.01, 0.4] # theta = [log10(D1), log10(D2), p12, p21]
    ll = loglikelihood(thetaguess, dr2, dt)
    print(ll)
     
    # Or, more efficiently, compute log likelihood pooling all tracks together
    dr2 = sqdis(allTracks) 
    llcombined = map(lambda track: loglikelihood(thetaguess, track, dt), dr2)
    print(sum(llcombined)) # combined log likeihood = sum of individual log likelihoods
     
    doMetropolis2(allTracks[:1000])

