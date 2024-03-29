import numpy as np
import math
import random
import Fileio
from .mcmc import logsum

dr = np.array(Fileio.getTrackFile())[0][:,[1,2]]
dr2 = dr[:,0]*dr[:,0]+dr[:,1]*dr[:,1]
tau = 0.1


def testLikely(theta):
    D = [theta[0],theta[1]]
    pi = [theta[3]/(theta[2]+theta[3]), theta[2]/(theta[2]+theta[3])]
    
    l = np.array([np.exp(0-dr2/(4*D[0]*tau))/(4*math.pi*D[0]*tau),np.exp(0-dr2/(4*D[1]*tau))/(4*math.pi*D[1]*tau)])
    l = np.transpose(l)
    #print l
    '''
    for step in dr2:
        elem = np.zeros((2),dtype=np.float64)
        for i in range(len(D)):
            elem[i] = math.exp(-step/(4*D[i]*tau))/(4*math.pi*D[i]*tau)
        l.append(elem[:])
    '''

    anolog = []
    anew = pi * l[0]
    anolog.append(1.0*anew)

    for j in range(1,len(dr2)):
        anew = np.zeros((2),dtype=np.float64)
        anew[0] = ( anolog[-1][0]*(1-theta[2]) + anolog[-1][1]*theta[3] ) * l[j][0]
        #print anew[0].dtype
        anew[1] = ( anolog[-1][1]*(1-theta[3]) + anolog[-1][0]*theta[2] ) * l[j][1]
        anolog.append(1.0*anew)

    #print D
    #print theta
    #for k in range(len(l)):
    #    if l[k][0] > 1 or l[k][0] < 0:
    #        print 0, dr2[k], l[k][0]
    #    if l[k][1] > 1 or l[k][1] < 0:
    #        print 1, dr2[k], l[k][1]
    #print anolog[-1]

    outfile = open("anolog.txt",'w')
    outfile.write("# iteration  dr[0]   dr[1]  dr2  l[0]   l[1]   anolog[0]  anolog[1] \n")
    for i in range(len(dr2)):
        outfile.write(str(i) + ' ' + str(dr[i,0]) + ' ' + str(dr[i,1]) + ' ')
        outfile.write(str(dr2[i]) + ' ' + str(l[i,0]) + ' ' + str(l[i,1]) + ' ')
        outfile.write(str(anolog[i][0]) + ' ' + str(anolog[i][1]) + '\n')
    outfile.close()
    return (anolog[-1][0]+anolog[-1][1])


def testLogLikely(theta):
    #Preliminary variable calculations
    D = [theta[0],theta[1]]
    pi = np.array([theta[3]/(theta[2]+theta[3]),theta[2]/(theta[2]+theta[3])])

    #single step likelyhoods
    l = np.array([0 - dr2/(4*D[0]*tau) - math.log(4*math.pi*D[0]*tau),0 - dr2/(4*D[1]*tau) - math.log(4*math.pi*D[1]*tau)])
    l = np.transpose(l)
    #print l

    #combining log-likelyhoods:
    alogs = []
    anew = pi
    try:
        anew = np.log(pi) + l[0]
    except ValueError:
        print(("pi is "+str(pi[0])+ ' ' + str(pi[1])))
        sys.exit(1)
    alogs.append(1.0*anew)
    print((anew,alogs[0]))

    for j in range(1,len(dr2)):
        #print j
        #print anew
            
        anew[0] = logsum(alogs[-1][0]+math.log(1-theta[2]), alogs[-1][1]+math.log(theta[3])) + l[j][0]
        anew[1] = logsum(alogs[-1][0]+math.log(theta[2]), alogs[-1][1]+math.log(1-theta[3])) + l[j][1]
        if anew[0] < -705:
            break
        alogs.append(1.0*anew)
        #print alogs
    print((alogs[0], len(alogs)))

    outfile = open("alogs.txt",'w')
    outfile.write("# iteration  dr[0]   dr[1]  dr2  l[0]   l[1]   anolog[0]  anolog[1] \n")
    for i in range(len(alogs)):
        outfile.write(str(i) + ' ' + str(dr[i,0]) + ' ' + str(dr[i,1]) + ' ')
        outfile.write(str(dr2[i]) + ' ' + str(l[i,0]) + ' ' + str(l[i,1]) + ' ')
        outfile.write(str(alogs[i][0]) + ' ' + str(alogs[i][1]) + '\n')
    outfile.close()
        
    return logsum(alogs[-1][0], alogs[-1][1])



if __name__=="__main__":
    print((testLikely([3,2,0.1,0.1])))
    print((testLogLikely([3,2,0.1,0.1])))
