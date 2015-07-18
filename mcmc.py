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

#Global variables
dr = np.array(Fileio.getTrackFile())[0][:,[1,2]]
tau = 0.005  #Acquisition time in s

#Helpful variables
logtau = math.log(4*math.pi*tau)
logten = math.log(10)

dr2 = np.zeros((len(dr)))
for i in xrange(len(dr)):
    dr2[i] = dr[i,0]*dr[i,0] + dr[i,1]*dr[i,1]
'''
print dr2
print
'''

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
    #logp = [math.log(theta[2]), math.log(theta[3])]
    pi = [theta[3]/(theta[2]+theta[3]),theta[2]/(theta[2]+theta[3])]
    #logpi = [math.log(pi[0]),math.log(pi[1])]

    #single step likelyhoods
    l = []
    for step in dr2:
        elem = []
        for i in xrange(2):
            elem.append(0 - step/(4*D[i]*tau) - logten * theta[i] - logtau)
        l.append(elem[:])
        


    #combining log-likelyhoods:
    alogs = []
    anew = []
    try:
        anew.append(math.log(pi[0])+l[0][0])
        anew.append(math.log(pi[1])+l[0][1])
    except ValueError:
        print("pi is "+str(pi[0])+ ' ' + str(pi[1]))
        sys.exit(1)
    alogs.append(anew[:])

    for j in xrange(1,len(dr2)):
        #print j
        anew[0] = logsum(alogs[-1][0]+math.log(1-theta[2]), alogs[-1][1]+math.log(theta[3])) + l[j][0]
        anew[1] = logsum(alogs[-1][0]+math.log(theta[2]), alogs[-1][1]+math.log(1-theta[3])) + l[j][1]
        alogs.append(anew[:])
    '''
    print pi
    print
    print l
    print
    print alogs
    print
    '''
    return logsum(alogs[-1][0], alogs[-1][1])


def doMetropolis():
    N = 100000
    theta = []
    L = []
    vartheta = [1,1.0,0.0,0.0]
    theta.append(np.array([-1,-2,0.1,0.05]))
    proptheta = theta[-1][:]
    L.append(logLikelyhood(proptheta))
    Lmax = L[-1]
    
    outfile = open("hiddenMCMC.txt",'w')
    outfile.write("#Hidden Markov Chain Monte Carlo\n")
    outfile.write("# LogLikelyhood   log10(D1)  log10(D2)   p12   p21\n")

    for i in xrange(int(N/4)):
        for k in xrange(4):
            dt = np.zeros((4))
            l = 4 * i + k
            print l
            dt[k] = random.gauss(0, vartheta[k])
            if k in [2,3]:
                while proptheta[k] + dt[k] <= 0 or proptheta[k] + dt[k] > 1:
                    dt[k] = random.gauss(0,vartheta[k])

            proptheta = proptheta + dt
            
            Ltest = logLikelyhood(proptheta)

            if Ltest > L[-1]:
                theta.append(proptheta)
                L.append(Ltest)
                Lmax = Ltest
            else:
                u = random.random()
                #if False: 
                if math.log(u) < Ltest - L[-1]: #and math.log(u) < Ltest - Lmax:
                    theta.append(proptheta)
                else:
                    theta.append(theta[-1][:])
                    proptheta = theta[-1][:]
                L.append(Lmax) #!!!!! With this we are introducing a wrong
                               #method, but ensuring more stability
                               #towards the maximum!!!!
            outfile.write(str(L[-1]))
            for k in xrange(4):
                outfile.write(' ' + str(theta[-1][k]))
            outfile.write('\n')
            print L[-1], theta[-1][0], theta[-1][1], theta[-1][2], theta[-1][3]
    outfile.close()             # 
    #print Lmax, theta[-1][0], theta[-1][1]
    return theta, L




    
if __name__=="__main__":
    doMetropolis()
    print
    print "#"+str( logLikelyhood([-1,1,0.2,0.1]))
