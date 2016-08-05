import Detection.convertFiles as cF
import System.Fileio as FIO

import numpy as np
import scipy.signal as sig
from scipy import optimize
import matplotlib.pyplot as plt

def main():
    path = "/home/markus/LittleHelpers/LTOS/ExampleFiles/"
    image1 = np.array(FIO.readImage(path+"green0639.tif"))
    image1 = image1 - image1.mean()
    image2 = np.copy(image1[100:412,100:412])
    image2 -= image2.mean()
    image3 = np.array(FIO.readImage(path+"green0001.tif"))
    im3 = np.copy(image3[100:412,100:412])
    im3 -= im3.mean()
    binary1 = image1 > 0.05
    binary2 = image2 > 0.05
    '''
    plt.imshow(binary1[100:len(binary1)-100,100:len(binary1[0])-100],cmap="Greys_r")
    plt.show()
    plt.imshow(binary2[100:len(binary1)-100,100:len(binary1[0])-100],cmap="Greys_r")
    plt.show()
    compare = np.zeros((51,51))
    for a in xrange(len(compare)):
        for b in xrange(len(compare[0])):
            counter = 0.
            print a,b
            for i in xrange(150,len(binary1)-150,1):
                for j in xrange(150,len(binary1[i])-150,1):
                    compare[a,b] += float(binary1[i,j] == binary2[i-a+25,j-b+25])
                    counter += 1.
            compare[a,b] /= counter
    plt.imshow(compare,cmap="Greys_r")
    plt.show()
    '''
    im1 = np.zeros((100,100))
    for i in xrange(20,21,1):
        for j in xrange(20,21,1):
            im1[i,j] = 1
    im2 = np.zeros((100,100))
    for i in xrange(60,61,1):
        for j in xrange(60,61,1):
            im2[i,j] = 1
    corr = sig.correlate2d(image1,im3,mode="valid",boundary='symm')
    x,y = np.unravel_index(np.argmax(corr), corr.shape) # find the match
    print x,y

    fig1, (ax1,ax2,ax3) = plt.subplots(1,3)
    ax1.imshow(image1,cmap="Greys_r")
    ax2.imshow(image3,cmap="Greys_r")
    ax3.imshow(corr)
    plt.show()

    dat = np.copy(corr[x-5:x+5,y-5:y+5])
    mback = corr.mean()
    para = fitgaussian2d(dat,mback)
    print para
    return

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


if __name__=="__main__":
    main()
