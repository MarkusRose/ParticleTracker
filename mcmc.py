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

#Global variables
dr = np.zeros((1000,2))
tau = 0.03  #Acquisition time in s

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
    if a < -700 and b < -700:
        return -100000000
    elif a > 700 or b > 700:
        return -100000000
    return math.log(math.exp(a)+math.exp(b))

#Log-Likelyhood
def logLikelyhood(theta):
    #Preliminary variable calculations
    D = [10**theta[0],10**theta[1]]
    logp = [math.log(theta[2]), math.log(theta[3])]
    pi = [theta[3]/(theta[2]+theta[3]),theta[2]/(theta[2]+theta[3])]
    logpi = [math.log(pi[0]),math.log(pi[1])]

    #single step likelyhoods
    l = []
    for step in dr2:
        elem = []
        for i in xrange(2):
            elem.append(0 - step/(4*math.pi*D[i]) - logten * theta[i] - logtau)
        l.append(elem)


    #combining log-likelyhoods:
    anew = []
    anew.append(math.log(pi[0])+l[0][0])
    anew.append(math.log(pi[1])+l[0][1])

    for j in xrange(1,len(dr2)):
        #print j
        aprev = anew[:]
        anew[0] = logsum(aprev[0]+logp[0], aprev[1]+logp[1]) + l[j][0]
        anew[1] = logsum(aprev[0]+logp[0], aprev[1]+logp[1]) + l[j][1]
        
    return logsum(anew[0],anew[1])
    

def doMetropolis():
    N = 100000
    theta = []
    L = []
    vartheta = [0.01,0.01,0.001,0.001]
    theta.append([random.random(),random.random(),random.random(),random.random()])
    proptheta = theta[-1][:]
    L.append(logLikelyhood(proptheta))

    for i in xrange(int(N/4)):
        for k in xrange(4):
            dt = [0,0,0,0]
            l = 4 * i + k
            dt[k] = random.gauss(0, vartheta[k])

            for j in xrange(len(dt)):
                proptheta[j] += dt[j]
            
            L.append(logLikelyhood(proptheta))

            if L[-1] > L[-2]:
                theta.append(proptheta)
            else:
                u = random.random()
                if math.log(u) < L[-1] - L[-2]:
                    theta.append(proptheta)
                else:
                    theta.append(theta[-1][:])
                    proptheta = theta[-1][:]
            print L[-1], theta[-1]
    return theta, L




    
if __name__=="__main__":
    print logLikelyhood([.199999,0.30,0.318,0.866])
    doMetropolis()
