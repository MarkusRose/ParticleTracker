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
from time import gmtime, strftime
import matplotlib.pyplot as plt

# Function definitions


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
#  print rsquared
  loglike = np.array( [[-rsq/(4*D*tau) for D in [D1, D2]] for rsq in rsquared] ) - [log(D1*tau), log(D2*tau)]
  # Compute forward variable alpha (algorithm 2 - Das et al)
  logalpha = np.empty_like(loglike)
  logalpha[0,:] = logstatprob + loglike[0,:]
  for j in xrange(1, nsteps):
    logalpha[j,:] = map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:]) + loglike[j, :]
  return logsum(logalpha[-1,0], logalpha[-1, 1])


def segmentstate(theta, allTracks, particleID, tau=1.):
    # Select a track by particle ID (the last column) and extract particle positions
    dr = allTracks[allTracks[:,-1] == particleID][:, [1,2]]
    # Compute squared displacements for selected track
    rsquared = np.sum(dr**2, axis=1)
    # Extract parameters
    D1, D2 = 10**theta[0], 10**theta[1]
    p12, p21 = theta[2], theta[3]
    nsteps = np.size(rsquared, 0)
    logstatprob = np.log([p21/(p21 + p21), p12/(p12 + p21)])
    logtransprob = np.log([[1 - p12, p12], [p21, 1-p21]])
    # Compute single step log likelihoods (eq 19 - Das et al)
    #  print rsquared
    loglike = np.array( [[-rsq/(4*D*tau) for D in [D1, D2]] for rsq in rsquared] ) - [log(D1*tau), log(D2*tau)]
    # Compute forward variable alpha (algorithm 2 - Das et al)
    logalpha = np.empty_like(loglike)
    logalpha[0,:] = logstatprob + loglike[0,:]
    for j in xrange(1, nsteps):
        logalpha[j,:] = map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:]) + loglike[j, :]
    # Compute backward variable beta (algorithm 5 - Das et al)
    logbeta = np.empty_like(loglike)
    logbeta[nsteps-1,:] = [0,0]
    for j in xrange(1,nsteps,1):
        logbeta[nsteps-1-j,:] = map(logsum, logtransprob[:,0] + logbeta[nsteps-j,0] + loglike[nsteps-j,0], logtransprob[:,1] + logbeta[nsteps-j,1] + loglike[nsteps-j,1])
    stateprob = np.empty_like(loglike)
    for j in xrange(nsteps):
        stateprob[j,:] = logalpha[j,:] * logbeta[j,:]
    statemap = np.zeros((nsteps))
    for j in xrange(nsteps):
        if stateprob[j,0] < stateprob[j,1]:
            statemap[j] = 1
    return statemap


# Usage
def doMetropolisOrig(allTracks,folder,particleID):
    #print len(allTracks)
    # Select a track by particle ID (the last column) and extract particle positions
    dr = allTracks[allTracks[:,-1] == particleID][:, [1,2]]
    # Compute squared displacements for selected track
    dr2 = np.sum(dr**2, axis=1)
    #dr2 = sqdis(allTracks)
    n = 10000 #Number of MCMC steps
    s = np.array([0.01,0.01,0.01,0.01])
    
    thetaprop = np.array([0,-1,0.1,0.4])
    ll = loglikelihood(thetaprop, dr2, 1.)
    theta = []
    L = []
    theta.append(np.array(thetaprop))
    L.append(ll)

    outf = open("Anaout{:04d}.txt".format(particleID),'w')
    outf.write("# L logD1 LogD2 p12 p21 n\n")

    for i in xrange(int(np.floor(n/4.))):
        for k in xrange(4):
            l = 4*i + k
            print l
            dtheta = random.gauss(0,s[k])
            thetaprop = np.array(theta[-1])
            thetaprop[k] += dtheta
            ll = loglikelihood(thetaprop, dr2, 1.)
            if ll >= L[-1]:
                theta.append(np.array(thetaprop))
                L.append(ll)
            else:
                u = random.random()
                if log(u) <= ll - L[-1]:
                    theta.append(np.array(thetaprop))
                    L.append(ll)
                else:
                    theta.append(np.array(theta[-1]))
                    L.append(L[-1])
            outf.write("{:} {:} {:} {:} {:} {:}\n".format(L[-1],10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3], l))
    outf.close()
    return theta, L, n

