import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import scipy.ndimage.filters
from scipy import optimize
from PIL import Image
import sys

def gauss1d(coord,mean,std,intensity):
    x = np.arange(len(coord))
    return np.exp(-(x-1.*mean)**2/(2.*std**2))

def gauss2d(coord,mean,std,intensity):
    grid = np.mgrid[0:len(coord),0:len(coord[0])]
    return np.exp(-((grid[0]-1.*mean[0])**2+(grid[1]-1.*mean[1])**2)/(2.*std**2))*intensity

def addNoise(coord,sigtonoise):
    return np.random.normal(0,np.sqrt(1.*np.max(coord)/sigtonoise),size=(len(coord),len(coord[0])))


def fitgaussian2d(data, background_mean, user_moments = None):
    """Returns (height, amplitude, x, y, width_x, width_y) as a numpy array
    found by least squares fitting of gaussian variables:"""
    
    if user_moments == None:
        initial_params = image_moments(data, background_mean)
    else:
        initial_params = user_moments
    
    #ravel is a special case for "unraveling" higher dimensional arrays into 1D arrays
    errorfunction = lambda p: np.ravel((gaussian2d(*p)(*np.indices(data.shape)) - data))
    p, cov, infodict, errmsg, success = optimize.leastsq(errorfunction, initial_params, full_output=1)
    return p



def image_moments(data, mean_background):
    total = data.sum()
    Y,X = np.indices(data.shape)
  
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    
    col = data[:, int(x)]
    width_y = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    
    row = data[int(y), :]
    width_x = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    
    height = mean_background
    amplitude = data.max() - height
    
    return (height, amplitude, x, y, width_x, width_y)



def gaussian2d(height, amplitude, center_x, 
               center_y, width_x, width_y):
    """Return 2d gaussian lamda(x,y) function"""
    
    height = float(height)
    amplitude = float(amplitude)
    width_x = float(width_x)
    width_y = float(width_y)
    
    return (lambda x,y: height + 
            amplitude*np.exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2))


def radial_center(I):

    m = np.zeros(((len(I)-1)*(len(I[0])-1)))
    divI = np.zeros(((len(I)-1)*(len(I[0])-1)))
    d_kc = np.zeros(((len(I)-1)*(len(I[0])-1)))
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
            print i,j,k
            divI[k] = u**2 + v**2
            if u-v == 0:
                m[k] = 1e10
            else:
                m[k] = (u+v)/(u-v)
            d_kc[k] = np.sqrt((xmax-i)**2+(ymax-j)**2)
            if d_kc[k] == 0:
                d_kc[k] = 1e-2

    origar = np.array(divI,copy=True)
    divI = np.reshape(divI,(len(I)-1,len(I[0])-1))
    divI = scipy.ndimage.filters.convolve(divI,np.full((3,3),1))
    divI = divI.flatten()
    '''
    m = np.reshape(divI,(len(I)-1,len(I[0])-1))
    m = scipy.ndimage.filters.convolve(m,np.full((3,3),1))
    m = m.flatten()
    '''

    for k in xrange((len(I)-1)*(len(I[0])-1)):
        i = int(1.*k/(len(I[0])-1))
        j = k % (len(I[0])-1)
        print i,j
        w[k] = divI[k]/d_kc[k]
        W += w[k]/(m[k]**2 + 1)
        M += m[k]*w[k]/(m[k]**2 + 1)
        M2 += m[k]**2 * w[k]/(m[k]**2 + 1)
        Wxy += w[k]/(m[k]**2 + 1) * (m[k]*(i+0.5) - (j+0.5))
        Mxy += m[k]*w[k]/(m[k]**2 + 1) * (m[k]*(i+0.5) - (j+0.5))

    delt = W * M2 - M**2
    xc = (Mxy * W - Wxy * M)/delt
    yc = (Mxy * M - Wxy * M2)/delt

    return xc, yc, np.reshape(divI,(len(I)-1,len(I[0])-1)),np.reshape(origar,(len(I)-1,len(I[0])-1))



if __name__=="__main__":

    size = 10

    mean = np.array([size/2.,size/2.])
    mean += np.random.random((2))*size/5. - size/10.
    std = 3
    intens = 100
    SNR = 100
    Background = 100

    I = np.zeros((size,size),dtype=np.float_)
    I = gauss2d(I,mean,std,intens)
    I += addNoise(I,SNR)
    I += Background
    I[I<0] = 0

    xc,yc,divI,oDI = radial_center(I)

    param = fitgaussian2d(I, Background)

    print xc,yc
    print param[2],param[3]
    print mean
    print np.array([xc,yc]) - np.array(mean)
    print np.array([param[2],param[3]]) - np.array(mean)

    sys.stdout.flush()

    imI = Image.fromarray(np.uint8(cm.gist_earth((I-np.min(I))/(np.max(I)-np.min(I)))*255))
    imDivI = Image.fromarray(np.uint8(cm.gist_earth((divI-np.min(divI))/(np.max(divI)-np.min(divI)))*255))
    imODI =  Image.fromarray(np.uint8(cm.gist_earth((oDI-np.min(oDI))/(np.max(oDI)-np.min(oDI)))*255))


    f = plt.figure(1)
    plt.imshow(imI)
    
    '''
    f2 = plt.figure(2)
    plt.imshow(imODI)
    '''

    f1 = plt.figure(3)
    plt.imshow(imDivI)

    #g = plt.figure(4)
    #plt.plot(I[int(mean[0])])

    #plt.show()

