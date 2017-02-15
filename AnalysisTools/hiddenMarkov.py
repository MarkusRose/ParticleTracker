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


def readHMMData(filename):
    infile = open(filename,'r')

    allhmm = []
    header = ""
    for line in infile:
        td = []
        if line[0] == "#":
            header = line[:]
            continue
        saver = line.split()
        for i in xrange(len(saver)):
            if i==9:
                td.append(saver[i])
            else:
                td.append(float(saver[i]))
        allhmm.append(td)
    return allhmm, header


def trackLength(track):

    framestart = -1
    frameend = -1

    for part in track.track:
        if np.isnan(part['frame']) or part['frame'] == 0:
            continue
        elif framestart == -1:
            framestart = part['frame']
        else:
            frameend = part['frame']
    if framestart == -1:
        return 0
    elif frameend == -1:
        return 1
    return frameend - framestart


def displacements(tracks):
    displacements = []
    lengths = []
    for track in tracks:
        single_disp = []
        x = np.nan
        y = np.nan
        x_prev = np.nan
        y_prev = np.nan
        time_dis = 1
        part_id = track.id
        for i in xrange(len(track.track)):
            x = track.track[i]['x']
            y = track.track[i]['y']
            if not (np.isnan(x) or np.isnan(y)):
                if not (np.isnan(x_prev) or np.isnan(y_prev)):
                    for k in xrange(time_dis):
                        single_disp.append(np.array([(x-x_prev)/time_dis,(y-y_prev)/time_dis]))
                x_prev = x
                y_prev = y
                time_dis = 1
            else:
                time_dis += 1
        if len(single_disp) > 0:
            displacements.append([np.array(single_disp),part_id])
            lengths.append(trackLength(track))
    return displacements,lengths


def squaredDisplacements(tracks):

    disps,length = displacements(tracks)
    rsquared = []
    
    for tr in disps:
        rsquared.append([np.sum(tr[0]**2,axis=1),tr[1]])
    
    return rsquared,length
    


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


def segmentstate(theta, rsquared, particleID, tau=1.):
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
def doMetropolisOrig(dr2,particleID,MCsteps=10000):

    s = np.array([0.01,0.01,0.01,0.01])
    
    thetaprop = np.array([0,-1,0.1,0.4])
    ll = loglikelihood(thetaprop, dr2, 1.)
    theta = []
    L = []
    theta.append(np.array(thetaprop))
    L.append(ll)

    outf = open("hmmTrackAnalyzed-{:}.txt".format(particleID),'w')
    outf.write("# L logD1 LogD2 p12 p21 n\n")

    for i in xrange(int(np.floor(MCsteps/4.))):
        for k in xrange(4):
            l = 4*i + k
            #print l
            sys.stdout.flush()
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
    return theta, L, MCsteps


def runHiddenMarkov(tracks,MCMC=10000):

    rsq,lengths = squaredDisplacements(tracks)
    averagingStart = min(2000,MCMC)
    if averagingStart == MCMC:
        averagingStart /= 5

    Thetas = []
    for r2 in rsq:
        theta, L, nurun = doMetropolisOrig(r2[0],r2[1],MCMC)
        theta = np.array(theta)
        D1 = 10**theta[:,0]
        D2 = 10**theta[:,1]
        p12 = theta[:,2]
        p21 = theta[:,3]
        
        '''
        fig1, (ax1,ax2) = plt.subplots(2,1)
        ax1.plot(D1,'gx')
        ax1.plot(D2,'rx')
        ax2.plot(p12,'gx')
        ax2.plot(p21,'rx')
        plt.show()
        '''
        
        thetaMean = [np.mean(D1[averagingStart:]),np.mean(D2[averagingStart:]),np.mean(p12[averagingStart:]), np.mean(p21[averagingStart:])]
        thetaSTD = [np.std(D1[averagingStart:]),np.std(D2[averagingStart:]),np.std(p12[averagingStart:]), np.std(p21[averagingStart:])]
        Thetas.append(thetaMean + thetaSTD + [r2[1]])
        print thetaMean
        
        statemap = segmentstate(thetaMean, r2[0],r2[1])
        trackout = open("hmmTrackstates-{:}.txt".format(r2[1]),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
    outthetaf = open("hmmAveragedData.txt",'w')
    outthetaf.write("#  D1 D2 p12 p21 stds: D1 D2 p12 p21 tracklength particle-ID\n")
    for i in xrange(len(Thetas)):
        counter = 0
        for elem in Thetas[i]:
            if counter != 8:
                outthetaf.write("{:} ".format(elem))
            else:
                outthetaf.write("{:} ".format(lengths[i]))
            counter += 1
        outthetaf.write("\n")
    outthetaf.close()
    
    return Thetas


