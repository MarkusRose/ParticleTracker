#================================
#=== Hidden Markov Model MCMC   
#================================

'''Done after the paper of Das (2009)
Using displacements {dr} of a track of length N to determine D1, D2, p12,
p21 of heterogeneous brownian motion.'''

#Packages
import numpy as np
import math
import random
import Fileio
import sys


'''read-in trajectory'''
def getTrackFile(filename):
    alltracks = []
    track = []
    particle = []
    infile = open(filename,'r')
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


#set error output
np.seterr()
#Global variables
dr = np.array(getTrackFile("Tracks.txt"))[0][:,[1,2]]
tau = 0.1  #Acquisition time in s

#Helpful variables
logtau = math.log(4*math.pi*tau)
logten = math.log(10)

dr2 = np.zeros((len(dr)))
for i in xrange(len(dr)):
    dr2[i] = dr[i,0]*dr[i,0] + dr[i,1]*dr[i,1]


# Functions
#-----------

#log(e^a+e^b)
def logsum(a,b):
    #if exponents exeed or are smaller than certain values, stop the program
    if a < -700 and b < -700:
        return -100000000
    elif a > 700 or b > 700:
        return -100000000
    return math.log(math.exp(a)+math.exp(b))

#Log-Likelihood
def loglikelihood(theta):
    #Preliminary variable calculations
    D = [10**theta[0],10**theta[1]]
    pi = [theta[3]/(theta[2]+theta[3]),theta[2]/(theta[2]+theta[3])]
    
    #single step loglikelihoods
    l = []
    for step in dr2:
        elem = []
        for i in xrange(2):
            #loglikelihood for a single random walk step
            elem.append(0 - step/(4*D[i]*tau) - logten * theta[i] - logtau)
        l.append(elem[:])
        
    #combining log-likelihoods:
    #forward variables from forward-backward algorithm
    alogs = []
    anew = []
    try:
        anew.append(math.log(pi[0])+l[0][0])
        anew.append(math.log(pi[1])+l[0][1])
    except ValueError:
        print("pi is "+str(pi[0])+ ' ' + str(pi[1]))
        #make sure, that pi[0] or pi[1] was not zero before log!!!
        sys.exit(1)
    alogs.append(anew[:])

    for j in xrange(1,len(dr2)):
        #print j
        anew[0] = logsum(alogs[-1][0]+math.log(1-theta[2]), alogs[-1][1]+math.log(theta[3])) + l[j][0]
        anew[1] = logsum(alogs[-1][0]+math.log(theta[2]), alogs[-1][1]+math.log(1-theta[3])) + l[j][1]
        alogs.append(anew[:])
    return logsum(alogs[-1][0], alogs[-1][1])

#Likelihood
def likelihood(theta):
    D = [10**theta[0],10**theta[1]]
    pi = [theta[3]/(theta[2]+theta[3]), theta[2]/(theta[2]+theta[3])]
    
    #single step likelihoods
    l = []
    for step in dr2:
        elem = np.zeros((2),dtype=np.float64)
        for i in xrange(len(D)):
            #likelihood for a single random walk step
            elem[i] = math.exp(-step/(4*D[i]*tau))/(4*math.pi*D[i]*tau)
        l.append(elem[:])

    #combining likelihoods
    #forward variables from forward-backward algorithm
    anolog = []
    anew = np.zeros((2),dtype=np.float64)
    anew[0] = (pi[0]*l[0][0])
    anew[1] = (pi[1]*l[0][1])
    anolog.append(1.0*anew[:])

    for j in xrange(1,len(dr2)):
        anew = np.zeros((2),dtype=np.float64)
        anew[0] = ( anolog[-1][0]*(1-theta[2]) + anolog[-1][1]*theta[3] ) * l[j][0]
        #print anew[0].dtype
        anew[1] = ( anolog[-1][1]*(1-theta[3]) + anolog[-1][0]*theta[2] ) * l[j][1]
        anolog.append(1.0*anew)

    return (anolog[-1][0]+anolog[-1][1])


'''We use a sampling method as described in Das 2009 (random walk through 4-dim parameter space). '''

#sampling method after Das 2009
def doMetropolis(likelihoodmethod):
    N = 100000
    theta = []
    L = []
    vartheta = [0.1,0.1,0.0,0.0]
    theta.append(np.array([0.5,1,0.3,0.3]))
    proptheta = theta[-1][:]
    L.append(likelihoodmethod(proptheta))
    Lmax = L[-1]
    
    outfile = open("hiddenMCMC.txt",'w')
    outfile.write("#Hidden Markov Chain Monte Carlo\n")
    outfile.write("# Loglikelihood   log10(D1)  log10(D2)   p12   p21\n")

    #Algorithm 3 from Das 2009:
    for i in xrange(int(N/4)):
        for k in xrange(4):
            dt = np.zeros((4))
            l = 4 * i + k
            print l
            dt[k] = random.gauss(0, vartheta[k])
            if k in [2,3]:
                while proptheta[k] + dt[k] <= 0 or proptheta[k] + dt[k] > 1:
                    dt[k] = random.gauss(0,vartheta[k])
            else:
                while proptheta[k] + dt[k] < 0:
                    dt[k] = random.gauss(0,vartheta[k])

            proptheta = proptheta + dt
            
            Ltest = likelihoodmethod(proptheta)

            if Ltest > L[-1]:
                theta.append(proptheta)
                L.append(Ltest)
            else:
                u = random.random()
                
                if math.log(u) < Ltest - L[-1]:
                    theta.append(proptheta)
                    L.append(Ltest)
                else:
                    theta.append(theta[-1][:])
                    proptheta = theta[-1][:]
                    L.append(L[-1]) 
            outfile.write(str(L[-1]))
            for k in xrange(4):
                outfile.write(' ' + str(theta[-1][k]))
            outfile.write('\n')
            #print L[-1], theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]
    outfile.close()
    #print Lmax, theta[-1][0], theta[-1][1]
    return theta, L

    

    
if __name__=="__main__":

    #Loglikelihood True/False
    bloglikelihood = True

    if bloglikelihood:
        doMetropolis(loglikelihood)
    else:
        doMetropolis(likelihood)
