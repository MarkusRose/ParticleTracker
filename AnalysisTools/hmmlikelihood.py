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

def importTracks(filename):
    '''Import tracks from csv file'''
    with open(filename) as f:
        csvdata = csv.reader(f)
        next(csvdata, None) # skip header
        return np.array( [list(map(float, row)) for row in csvdata] )

#read in Tracks
def readSimTrack(infile):
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
        track.append(np.array(list(map(float,line.split()))))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track
    return tracks

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
        track.append(np.array(list(map(float,line.split()))))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    outtracks = []
    count = 0
    for t in tracks:
        count += 1
        outtrack = [] 
        pox = 0
        poy = 0
        prevx = t[0][1]
        prevy = t[0][2]
        for i in range(1,len(t),1):
            dx = t[i][1]-prevx
            prevx = t[i][1]
            dy = t[i][2]-prevy
            prevy = t[i][2]
            outtrack.append([t[i][0],dx,dy,count])
        outtracks.append(np.array(outtrack))
    print((len(outtracks)))
    return np.array(outtracks)


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
  for j in range(1, nsteps):
    logalpha[j,:] = list(map(logsum, logalpha[j-1,0] + logtransprob[0,:], logalpha[j-1,1] + logtransprob[1,:])) + loglike[j, :]
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

    for i in range(int(np.floor(n/4.))):
        for k in range(4):
            l = 4*i + k
            print(l)
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

def doMetropolis3(allTracks,folder,particleID):

    #print len(allTracks)
    # Select a track by particle ID (the last column) and extract particle positions
    dr = allTracks[allTracks[:,-1] == particleID][:, [1,2]]
    # Compute squared displacements for selected track
    dr2 = np.sum(dr**2, axis=1)
    #dr2 = sqdis(allTracks)


    dt = 1.
    theta = []
    L = []
    vartheta = np.array([4,4,0.2,0.2])
    scalingfactor = 2.0
    theta.append(np.array([-3,-5,0.1,0.1]))
    proptheta = theta[-1][:]

    ll = loglikelihood(proptheta, dr2, dt)
    L.append(ll)

    #llcombined = map(lambda track: loglikelihood(proptheta, track, dt), dr2)
    #L.append(sum(llcombined))
    
    outfile = open(folder+"/hiddenMCMC2" + strftime("%Y%m%d%H%M%S", gmtime()) + ".txt",'w')
    outfile.write("#Hidden Markov Chain Monte Carlo\n")
    outfile.write("# LogLikelyhood   D1  D2    p12    p21    dD1    dD2   dp12    dp21 nuruns\n")
    outfile.write(str(L[-1]) + ' ' + str(theta[-1][0]) + ' ' + str(theta[-1][1]) + '\n')
    outpropsf = open("proposedHMM" + strftime("%Y%m%d%H%M%S", gmtime()) + ".txt",'w')
    outpropsf.write("# LogLikelyhood   theta1  theta2   theta3   theta4 \n")

    breakout = False
    
    i = 0
    nuruns = 0
    while True:
        Lmax = L[-1]
        index = 0
        props = []
        props.append([Lmax, theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]])
        j = 0
        #for j in range(100):
        while j < 100 or Lmax <= L[-1]:
            nuruns += 1
            dtheta = np.zeros((4))
            #proptheta = theta[-1]
            for l in range(4):
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
            for l in range(len(props[-1])):
                outpropsf.write(str(props[-1][l])+' ')
            outpropsf.write("\n")
            if Lmax < Ltest:
                Lmax = Ltest
                index = j+1
            j+=1
            if j > 1000:
                breakout = True
                break
        #print j
        outpropsf.write("\n\n")
        theta.append(np.array([props[index][1],props[index][2],props[index][3],props[index][4]]))
        L.append(props[index][0])
        #print i
        i += 1
        outfile.write(str(L[-1]))
        for k in range(4):
            outfile.write(' ' + str(theta[-1][k]))
        for k in range(4):
            outfile.write(' ' + str(vartheta[k]))
        outfile.write(' ' + str(nuruns))
        outfile.write('\n')
        #print L[-1], 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
        flag = False
        if breakout:
            for l in range(len(vartheta)):
                if l in [2,3]:
                    vartheta[l] /= scalingfactor
                else:
                    vartheta[l] /= scalingfactor
            #print "TRUE", vartheta
            breakout = False
        else:
            if len(theta) < 2:
                continue
        #convergence criterium:
        if vartheta[0] < (0.01/np.log(10)) and vartheta[1] < (0.01/np.log(10)):
            break
    outfile.close()
    print("              RESULTS:")
    print(("          ", Lmax, 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]))
    
    return theta, L, nuruns

def main(folder,reps):
    allTracks2 = readTracks(folder+'/foundTracks.txt')
    anaTr = []
    for t in allTracks2:
        for p in t:
            anaTr.append(np.array(p))
    anaTr = np.array(anaTr)
    '''
    sha = allTracks2.shape
    allTracks = allTracks2.reshape(sha[0]*sha[1],sha[2])
    '''

    numparts = anaTr[-1][-1]
    outtheta = []
    runs = []
    counter = 1
    print(numparts)
    rawout = open("rawDataout.txt", 'w')
    rawout.write("# Analysis of Cel5A \n# D1  D2   p12  p21  nuruns\n")
    sumout = open("avHmmData.txt",'w')
    sumout.write("# Analysis of Cel5A \n# D1  D2   p12  p21  nuruns stds....\n")

    while counter-1 < numparts:
        rawout.write("# Track {:}\n".format(counter))
        avTheta = []
        avNuruns = []
        for k in range(reps):
            print(("    Run {:},{:}".format(counter,k+1)))
            theta,L,nuruns = doMetropolis3(anaTr,folder,counter)
            if theta[-1][0] > theta[-1][1]:
                results = np.array([theta[-1][1],theta[-1][0],theta[-1][3],theta[-1][2]])
            else:
                results = np.array(theta[-1])
            avTheta.append(np.array(results))
            avNuruns.append(nuruns)
            rawout.write("{:} {:} {:} {:} {:}\n".format(results[0], results[1], results[2], results[3], nuruns))
        thetaMean = np.mean(avTheta,axis=0)
        thetaStd = np.std(avTheta,axis=0)
        outtheta.append([np.array(thetaMean),np.array(thetaStd)])
        runs.append([np.mean(avNuruns),np.std(avNuruns)])
        sumout.write("{:} {:} {:} {:} {:} {:} {:} {:} {:} {:}\n"
                     .format(thetaMean[0], thetaMean[1], thetaMean[2], thetaMean[3], np.mean(avNuruns),thetaStd[0],thetaStd[1],thetaStd[2],thetaStd[3],np.std(avNuruns)))
        rawout.write("\n\n")
        statemap = segmentstate(thetaMean, anaTr, counter)
        trackout = open("trackstates{:04d}.txt".format(counter),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
        counter += 1
    return outtheta, runs
        


def testerFunction1(folder,runs):
    allTracks2 = readSimTrack(folder+'/foundTracks.txt')
    anaTr = []
    for t in allTracks2:
        for p in t:
            anaTr.append(np.array(p))
    anaTr = np.array(anaTr)
    '''
    sha = allTracks2.shape
    allTracks = allTracks2.reshape(sha[0]*sha[1],sha[2])
    '''
    Thetas = []
    for i in range(max(runs,anaTr[-1:-1])):
        theta, L, nurun = doMetropolisOrig(anaTr,folder,i)
        theta = np.array(theta)
        theta1 = 10**theta[:,0]
        theta2 = 10**theta[:,1]
        p12 = theta[:,2]
        p21 = theta[:,3]
        
        fig1, (ax1,ax2) = plt.subplots(2,1)
        ax1.plot(theta1,'gx')
        ax1.plot(theta2,'rx')
        
        ax2.plot(p12,'gx')
        ax2.plot(p21,'rx')
        plt.show()
        
        thetaMean = [np.mean(theta1[1000:]),np.mean(theta2[1000:]),np.mean(p12[1000:]), np.mean(p21[1000:])]
        thetaSTD = [np.std(theta1[1000:]),np.std(theta2[1000:]),np.std(p12[1000:]), np.std(p21[1000:])]
        Thetas.append([np.array(thetaMean),np.array(thetaSTD)])
        print(thetaMean)
        
        statemap = segmentstate(thetaMean, anaTr, i)
        trackout = open("trackstates{:04d}.txt".format(0),'w')
        for elem in statemap:
            trackout.write("{:}\n".format(elem))
        trackout.close()
    outthetaf = open("AveragedData.txt",'w')
    outtheta.write("#  D1 D2 p12 p21 stds: D1 D2 p12 p21\n")
    for line in Thetas:
        for ones in line:
            for elem in ones:
                outtheta.write("{:} ".format(elem))
        outtheta.write("\n")
    outtheta.close()
    
    return
    
    
    
if __name__ == "__main__":
    #main(".",4)
    testerFunction1(".",100)
    
