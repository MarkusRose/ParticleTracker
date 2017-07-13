import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from PIL import Image
import sys

def gauss1d(coord,mean,std,intensity):
    x = np.arange(len(coord))
    return np.exp(-(x-1.*mean)**2/(2.*std**2))

def gauss2d(coord,mean,std,intensity):
    grid = np.mgrid[0:len(coord),0:len(coord[0])]
    return np.exp(-((grid[0]-1.*mean[0])**2+(grid[1]-1.*mean[1])**2)/(2.*std**2))*intensity

def addNoise(coord,sigtonoise):
    return np.random.normal(0,np.sqrt(1.*np.max(coord)**2/sigtonoise),size=(len(coord),len(coord[0])))

def radial_center(I):

    m = np.zeros(((len(I)-1)*(len(I[0])-1)))
    divI = np.zeros(((len(I)-1)*(len(I[0])-1)))
    w = np.zeros(((len(I)-1)*(len(I[0])-1)))

    W = 0
    M = 0
    M2 = 0
    Wxy = 0
    Mxy = 0

    xmax,ymax = np.unravel_index(I.argmax(),I.shape)
    
    #print range(len(I)-1)
    #print range(len(I[0])-1)
    for i in xrange(len(I)-1):
        for j in xrange(len(I[0])-1):
            k = j + i*(len(I[0])-1)
            u = I[i+1,j+1]-I[i,j]
            v = I[i,j+1]-I[i+1,j]
            #print u-v
            #print i,j,k
            divI[k] = u**2 + v**2
            if u-v == 0:
                m[k] = 1e10
            else:
                m[k] = (u+v)/(u-v)
            d_kc = np.sqrt((xmax-i)**2+(ymax-j)**2)
            if d_kc == 0:
                d_kc = 1e-2
            w[k] = divI[k]/d_kc
            W += w[k]/(m[k]**2 + 1)
            M += m[k]*w[k]/(m[k]**2 + 1)
            M2 += m[k]**2 * w[k]/(m[k]**2 + 1)
            Wxy += w[k]/(m[k]**2 + 1) * (m[k]*(i+0.5) - (j+0.5))
            Mxy += m[k]*w[k]/(m[k]**2 + 1) * (m[k]*(i+0.5) - (j+0.5))

    delt = W * M2 - M**2
    xc = (Mxy * W - Wxy * M)/delt
    yc = (Mxy * M - Wxy * M2)/delt

    return xc, yc, np.reshape(divI,(len(I)-1,len(I[0])-1))



if __name__=="__main__":

    size = 20

    mean = np.array([size/2.,size/2.])
    mean += np.random.random((2))*4. - 2.
    std = 2
    intens = 100
    SNR = 30
    Background = 10000

    I = np.zeros((size,size),dtype=np.float_)
    I = gauss2d(I,mean,std,intens)
    I += addNoise(I,SNR)
    I += Background
    I[I<0] = 0

    xc,yc,divI = radial_center(I)

    print xc,yc
    print mean
    print np.array([xc,yc]) - np.array(mean)

    sys.stdout.flush()

    imI = Image.fromarray(np.uint8(cm.gist_earth((I-np.min(I))/(np.max(I)-np.min(I)))*255))
    imDivI = Image.fromarray(np.uint8(cm.gist_earth((divI-np.min(divI))/(np.max(divI)-np.min(divI)))*255))

    f = plt.figure(1)
    plt.imshow(imI)

    f1 = plt.figure(3)
    plt.imshow(imDivI)

    g = plt.figure(2)
    plt.plot(I[int(mean[0])])

    plt.show()
