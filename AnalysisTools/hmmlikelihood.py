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

    outtracks = []
    count = 0
    for t in tracks:
        count += 1
        outtrack = [] 
        pox = 0
        poy = 0
        prevx = t[0][1]
        prevy = t[0][2]
        for i in xrange(1,len(t),1):
            dx = t[i][1]-prevx
            prevx = t[i][1]
            dy = t[i][2]-prevy
            prevy = t[i][2]
            outtrack.append([t[i][0],dx,dy,count])
        outtracks.append(np.array(outtrack))
    print len(outtracks)
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
    logbeta = np.emtpy_like(loglike)
    logbeta[nsteps-1,:] = [0,0]
    for j in xrange(1,nsteps,1):
        logbeta[nsteps-1-j,:] = map(logsum, logtransprob[:,0] + logbeta[nsteps-j,0] + loglike[nsteps-j,0], logtransprob[:,1] + logbeta[nsteps-j,1] + loglike[nsteps-j,1])
    stateprob = np.emtpy_like(loglike)
    for j in xrange(nsteps):
        stateprob[j,:] = logalpha[j,:] * logbeta[j,:]
    statemap = np.zeros((nsteps))
    for j in xrange(nsteps):
        if stateprob[j,0] < stateprob[j,1]:
            statemap[j] = 1
    return statemap


# Usage


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
        #for j in xrange(100):
        while j < 100 or Lmax <= L[-1]:
            nuruns += 1
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
        for k in xrange(4):
            outfile.write(' ' + str(theta[-1][k]))
        for k in xrange(4):
            outfile.write(' ' + str(vartheta[k]))
        outfile.write(' ' + str(nuruns))
        outfile.write('\n')
        #print L[-1], 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
        flag = False
        if breakout:
            for l in xrange(len(vartheta)):
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
    print "              RESULTS:"
    print "          ", Lmax, 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
    
    return theta, L, nuruns

def main(folder):
    allTracks2 = readTracks(folder+'/foundTracksCel5A.txt')
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
    print numparts
    rawout = open("rawDataout.txt", 'w')
    rawout.write("# Analysis of Cel5A \n# D1  D2   p12  p21  nuruns\n")

    while counter-1 < numparts:
        print "    Run {:}".format(counter)
        theta,L,nuruns = doMetropolis3(anaTr,folder,counter)
        if theta[-1][0] > theta[-1][1]:
            results = np.array([theta[-1][1],theta[-1][0],theta[-1][3],theta[-1][2]])
        else:
            results = np.array(theta[-1])
        rawout.write("{:} {:} {:} {:} {:}\n".format(results[0], results[1], results[2], results[3], nuruns))
        outtheta.append(results)
        runs.append(nuruns)
        counter += 1
    return outtheta, runs
        


def testerFunction1():
    # Import all tracks
    #allTracks = importTracks('foundTracks.csv')
    allTracks2 = np.array(readTracks('SimulatedTracks/010-20-30/foundTracks.txt'))
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
     
    doMetropolis3(allTracks[:1000])



if __name__ == "__main__":
    main(".")
    



def doMetropolis2(allTracks):

    print len(allTracks)
    
    # Select a track by particle ID (the last column) and extract particle positions
    particleID = 0
    dr = allTracks[allTracks[:,-1] == particleID][:, [1,2]]
    
    # Compute squared displacements for selected track
    dr2 = np.sum(dr**2, axis=1)

    #dr2 = sqdis(allTracks)


    dt = 1.
    theta = []
    L = []
    vartheta = np.array([4,4,0.2,0.2])
    minvarp = 0.005
    minvarD = 0.0005/dt
    theta.append(np.array([-3,-5,0.1,0.1]))
    proptheta = theta[-1][:]

    ll = loglikelihood(proptheta, dr2, dt)
    L.append(ll)

    #llcombined = map(lambda track: loglikelihood(proptheta, track, dt), dr2)
    #L.append(sum(llcombined))
    
    outfile = open("hiddenMCMC2.txt",'w')
    outfile.write("#Hidden Markov Chain Monte Carlo\n")
    outfile.write("# LogLikelyhood   D1  D2    p12    p21    dD1    dD2   dp12    dp21\n")
    outfile.write(str(L[-1]) + ' ' + str(theta[-1][0]) + ' ' + str(theta[-1][1]) + '\n')
    outpropsf = open("proposedHMM.txt",'w')
    outpropsf.write("# LogLikelyhood  theta1 theta2 theta3 theta4 \n")

    breakout = False
    
    i = 0
    numbreakers = 0
    numminvar = 0
    while True:
        Lmax = L[-1]
        index = 0
        props = []
        props.append([Lmax, theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]])
        j = 0
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
            if j > 1000:
                breakout = True
                break
        print j
        outpropsf.write("\n\n")
        theta.append(np.array([props[index][1],props[index][2],props[index][3],props[index][4]]))
        L.append(props[index][0])
        print i
        i += 1
        outfile.write(str(L[-1]))
        for k in xrange(4):
            outfile.write(' ' + str(theta[-1][k]))
        for k in xrange(4):
            outfile.write(' ' + str(vartheta[k]))
        outfile.write('\n')
        print L[-1], 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
        flag = False
        if breakout:
            numbreakers += 1
            flag = True
            for l in xrange(len(vartheta)):
                if l in [2,3]:
                    if vartheta[l] > minvarp**2:
                        vartheta[l] /= 2.0
                        flag = flag and False
                    else:
                        vartheta[l] = minvarp**2
                        flag = flag and True
                else:
                    if (10**(theta[-1][l]+np.sqrt(vartheta[l]))-10**(theta[-1][l])) > minvarD*2:
                        vartheta[l] /= 2.0
                        flag = flag and False
                    else:
                        vartheta[l] = (np.log10(minvarD + 10**(theta[-1][l]))-theta[-1][l])**2
                        flag = flag and True
            if flag:
                numminvar += 1
            else:
                numminvar = 0
            print "TRUE", vartheta
            print numbreakers, numminvar, flag
            breakout = False
        else:
            if len(theta) < 2:
                continue
            for l in xrange(len(theta[-1])):
                if l in [2,3]:
                    if (theta[-1][l] - theta[-2][l])**2 > minvarp:
                        numbreakers = 0
                else:
                    if (theta[-1][l] - theta[-2][l])**2 > minvarp:
                        numbreakers = 0
        if numbreakers > 100 or numminvar >= 10:
            break
    outfile.close()
    print "RESULTS:"
    print Lmax, 10**theta[-1][0], 10**theta[-1][1], theta[-1][2], theta[-1][3]
    
    return theta, L
