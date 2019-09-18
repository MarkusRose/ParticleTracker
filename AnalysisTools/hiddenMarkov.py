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
import time
import matplotlib.pyplot as plt
import os

import Detection.ctrack as ctrack

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
        for i in range(len(saver)):
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
    part_ids = []
    for track in tracks:
        single_disp = []
        x = np.nan
        y = np.nan
        x_prev = np.nan
        y_prev = np.nan
        time_dis = 1
        part_id = track.id
        for i in range(len(track.track)):
            x = track.track[i]['x']
            y = track.track[i]['y']
            if not (np.isnan(x) or np.isnan(y)):
                if not (np.isnan(x_prev) or np.isnan(y_prev)):
                    for k in range(time_dis):
                        single_disp.append(np.array([(x-x_prev)/time_dis,(y-y_prev)/time_dis]))
                x_prev = x
                y_prev = y
                time_dis = 1
            else:
                time_dis += 1
        if len(single_disp) > 0:
            displacements.append([np.array(single_disp),part_id])
            part_ids.append(part_id)
            lengths.append(trackLength(track))
    return displacements,lengths,part_ids


def squaredDisplacements(tracks):

    disps,length,part_ids = displacements(tracks)
    rsquared = []
    
    for tr in disps:
        rsquared.append([np.sum(tr[0]**2,axis=1),tr[1]])
    
    return rsquared,length,part_ids
    


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
  for j in range(1, nsteps):
    logalpha[j,:] = list(map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:])) + loglike[j, :]
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
    for j in range(1, nsteps):
        logalpha[j,:] = list(map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:])) + loglike[j, :]
    # Compute backward variable beta (algorithm 5 - Das et al)
    logbeta = np.empty_like(loglike)
    logbeta[nsteps-1,:] = [0,0]
    for j in range(1,nsteps,1):
        logbeta[nsteps-1-j,:] = list(map(logsum, logtransprob[:,0] + logbeta[nsteps-j,0] + loglike[nsteps-j,0], logtransprob[:,1] + logbeta[nsteps-j,1] + loglike[nsteps-j,1]))
    stateprob = np.empty_like(loglike)
    for j in range(nsteps):
        stateprob[j,:] = logalpha[j,:] * logbeta[j,:]
    statemap = np.zeros((nsteps))
    for j in range(nsteps):
        if stateprob[j,0] < stateprob[j,1]:
            statemap[j] = 1
    return statemap

def preMetropolis(dr2,theta,L,outf,MCsteps=10000,thetastd=[0.001,0.001,0.01,0.01],thetaguess=[0,-1,0.1,0.4],hot=0,ViewLive=False):
    s = np.array(thetastd)
    

    for i in range(int(np.floor(MCsteps/4.))):
        for k in range(4):
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
                if hot:
                    u = random.random()
                    if log(u) <= (ll - L[-1])*hot:
                        theta.append(np.array(thetaprop))
                        L.append(ll)
                    else:
                        theta.append(np.array(theta[-1]))
                        L.append(L[-1])
                else:
                    theta.append(np.array(theta[-1]))
                    L.append(L[-1])

            if ViewLive:
                if (len(L)+1) % 1000 == 0:
                    fig = plt.figure(1,figsize=(10,5))
                    fig.subplots_adjust(hspace=.3,wspace=.3)
                    plt.clf()
                    plt.subplot(231)
                    plt.scatter(np.arange(len(L)),L)
                    plt.ylabel("Likelihood")
                    plt.xlabel("Steps")
                    plt.subplot(232)
                    plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,0]*np.log(10)))
                    plt.ylabel("D1")
                    plt.xlabel("Steps")
                    plt.subplot(233)
                    plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,1]*np.log(10)))
                    plt.ylabel("D2")
                    plt.xlabel("Steps")
                    plt.subplot(235)
                    plt.scatter(np.arange(len(L)),np.array(theta)[:,2])
                    plt.ylabel("p12")
                    plt.xlabel("Steps")
                    plt.subplot(236)
                    plt.scatter(np.arange(len(L)),np.array(theta)[:,3])
                    plt.ylabel("p21")
                    plt.xlabel("Steps")
                    plt.pause(0.1)
            if l % 1000 == 0:            
                outf.write("{:} {:} {:} {:} {:} {:} {:}\n".format(L[-1],10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3], l))
    return theta, L, MCsteps


# Usage
def doMetropolisOrig(dr2,particleID,MCsteps=100000,path='.',thetastd=[0.01,0.01,0.01,0.01],thetaguess=[0,-1,0.1,0.4],hot=1,ViewLive=False):

    s = np.array(thetastd)
    
    thetaprop = np.array(thetaguess)
    ll = loglikelihood(thetaprop, dr2, 1.)
    if np.isnan(ll):
        thetaprop = np.array([-1,-2,0.1,0.5])
        ll = loglikelihood(thetaprop, dr2, 1.)
    theta = []
    L = []
    theta.append(np.array(thetaprop))
    L.append(ll)

    outf = open(path+"/hmmTrackAnalyzed-{:}.txt".format(particleID),'w')
    outf.write("# L logD1 LogD2 p12 p21 n\n")
    if ViewLive:
        plt.ion()

    theta, L, junk = preMetropolis(dr2,theta,L,outf,MCsteps=5000,thetastd=[0.01,0.01,0.00,0.00],thetaguess=thetaguess,hot=0,ViewLive=ViewLive)
    printThetaOut(theta[-1])
    theta, L, junk = preMetropolis(dr2,theta,L,outf,MCsteps=5000,thetastd=[0.00,0.00,0.05,0.05],thetaguess=theta[-1],hot=0,ViewLive=ViewLive)
    printThetaOut(theta[-1])
    for i in range(int(np.floor(MCsteps/4.))):
        for k in range(4):
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
                if hot:
                    u = random.random()
                    if log(u) <= (ll - L[-1])*hot:
                        theta.append(np.array(thetaprop))
                        L.append(ll)
                    else:
                        theta.append(np.array(theta[-1]))
                        L.append(L[-1])
                else:
                    theta.append(np.array(theta[-1]))
                    L.append(L[-1])

            if ViewLive:
                if (len(L)+1) % 1000 == 0:
                    fig = plt.figure(1,figsize=(10,5))
                    fig.subplots_adjust(hspace=.3,wspace=.3)
                    plt.clf()
                    plt.subplot(231)
                    plt.scatter(np.arange(len(L)),L)
                    plt.ylabel("Likelihood")
                    plt.xlabel("Steps")
                    plt.subplot(232)
                    plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,0]*np.log(10)))
                    plt.ylabel("D1")
                    plt.xlabel("Steps")
                    plt.subplot(233)
                    plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,1]*np.log(10)))
                    plt.ylabel("D2")
                    plt.xlabel("Steps")
                    plt.subplot(235)
                    plt.scatter(np.arange(len(L)),np.array(theta)[:,2])
                    plt.ylabel("p12")
                    plt.xlabel("Steps")
                    plt.subplot(236)
                    plt.scatter(np.arange(len(L)),np.array(theta)[:,3])
                    plt.ylabel("p21")
                    plt.xlabel("Steps")
                    plt.pause(0.1)
            if l % 1000 == 0:            
                outf.write("{:} {:} {:} {:} {:} {:}\n".format(L[-1],10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3], l))
    if not ViewLive:
        fig = plt.figure(1,figsize=(10,5))
        fig.subplots_adjust(hspace=.3,wspace=.3)
        plt.clf()
        plt.subplot(231)
        plt.scatter(np.arange(len(L)),L)
        plt.ylabel("Likelihood")
        plt.xlabel("Steps")
        plt.subplot(232)
        plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,0]*np.log(10)))
        plt.ylabel("D1")
        plt.xlabel("Steps")
        plt.subplot(233)
        plt.scatter(np.arange(len(L)),np.exp(np.array(theta)[:,1]*np.log(10)))
        plt.ylabel("D2")
        plt.xlabel("Steps")
        plt.subplot(235)
        plt.scatter(np.arange(len(L)),np.array(theta)[:,2])
        plt.ylabel("p12")
        plt.xlabel("Steps")
        plt.subplot(236)
        plt.scatter(np.arange(len(L)),np.array(theta)[:,3])
        plt.ylabel("p21")
        plt.xlabel("Steps")
    plt.savefig(path+"/Convergence{:}.png".format(particleID))
    plt.close()
    outf.close()
    return theta, L, MCsteps

def printThetaOut(theta):
    print("D1={:} ; D2={:} ; p12={:} ; p21={:}".format(10**theta[0],10**theta[1],theta[2],theta[3]))
    return

def runHiddenMarkov(tracks,MCMC=100000,ID=3,path='.',ViewLive=False):

    rsq,lengths,partid = squaredDisplacements(tracks)
    averagingStart = min(30000,MCMC)
    if averagingStart == MCMC:
        averagingStart = int(averagingStart/5)

    Thetas = []
    timepertrack = 0
    counter = 1
    for r2 in rsq:
        print("Running Track {:} of {:}".format(counter,len(rsq)))
        starttime = time.time()
        firstguess = np.random.normal([-1,-2,0.2,0.1],[0.3,1,0.1,0.1])
        printThetaOut(firstguess)
        theta, L, nurun = doMetropolisOrig(r2[0],r2[1],MCsteps=MCMC,path=path,thetastd=[0.005,0.005,0.01,0.01],thetaguess=firstguess,hot=100,ViewLive=ViewLive)
        theta = np.array(theta)
        D1 = 10**theta[:,0]
        D2 = 10**theta[:,1]
        p12 = theta[:,2]
        p21 = theta[:,3]
        
        thetaMean = [np.mean(D1[averagingStart:]),np.mean(D2[averagingStart:]),np.mean(p12[averagingStart:]), np.mean(p21[averagingStart:])]
        thetaSTD = [np.std(D1[averagingStart:]),np.std(D2[averagingStart:]),np.std(p12[averagingStart:]), np.std(p21[averagingStart:])]
        Thetas.append(thetaMean + thetaSTD + [r2[1]])
        #print(thetaMean)
        
        statemap = segmentstate(thetaMean, r2[0],r2[1])
        endtime = time.time()
        timepertrack += endtime - starttime
        trackout = open(path+"/hmmTrackstates-{:}.txt".format(r2[1]),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
        counter += 1
    date = strftime("%Y%m%d-%H%M%S")
    outthetaf = open(path+"/../hmmAveragedData-ID{:}_{:}.txt".format(ID,date),'w')
    outthetaf.write("#  D1 D2 p12 p21 stds: D1 D2 p12 p21 tracklength particle-ID\n")
    for i in range(len(Thetas)):
        counter = 0
        for elem in Thetas[i]:
            if counter != 8:
                outthetaf.write("{:} ".format(elem))
            else:
                outthetaf.write("{:} {:}".format(lengths[i],partid[i]))
            counter += 1
        outthetaf.write("\n")
    outthetaf.close()

    print("Average time needed for {:} tracks:  {:} s".format(len(rsq),timepertrack/len(rsq)))
    print("Average track length: {:} +- {:}".format(np.mean(lengths),np.std(lengths)))
    
    return Thetas

def doHMM(trackfile,montecarlo=100000,SR=0,ViewLive=False):

    part_tracks,part_list = ctrack.readTrajectoriesFromFile(trackfile)

    #make file path for save files. making sure not to override existing analysis
    filepath = os.path.split(trackfile)[0]
    trackfilename = os.path.split(trackfile)[1]
    if len(trackfilename) > 35:
        path = os.path.join(filepath,"HiddenMarkov_"+trackfilename[12:-4])
    else:
        path = os.path.join(filepath,"HiddenMarkov")
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        path = path +"-"+strftime("%Y%m%d-%H%M%S")
        os.mkdir(path)
    subfolder="Identifier-{:}".format(SR)
    subpath = os.path.abspath(os.path.join(path,subfolder))
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.path.isdir(subpath):
        os.mkdir(subpath)
    print(path)
    sys.stdout.flush()

    print("Running HMM")
    print("{:} Tracks found".format(len(part_tracks)))
    sys.stdout.flush()

    thetas = runHiddenMarkov(part_tracks,MCMC=montecarlo,ID=SR,path=subpath,ViewLive=ViewLive)

    return thetas


