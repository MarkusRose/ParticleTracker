import Detection.convertFiles as cF
import System.Fileio as FIO

import numpy as np
import scipy.signal as sig
from scipy import optimize
import matplotlib.pyplot as plt
import os
import glob

def correlateTwoImages(image1,image2,cutwindow):
    im1 = image1 - image1.mean()
    im2 = np.copy(image2[cutwindow:len(image2)-cutwindow,cutwindow:len(image2[0])-cutwindow])
    im2 -= im2.mean()
    corr = sig.correlate2d(im1,im2,mode="valid",boundary='symm')
    x,y = np.unravel_index(np.argmax(corr), corr.shape) # find the match
    print x,y

    fig1, (ax1,ax2,ax3) = plt.subplots(1,3)
    ax1.imshow(image1,cmap="Greys_r")
    ax2.imshow(image2,cmap="Greys_r")
    ax3.imshow(corr)
    plt.show()

    fitbox = ( x-min(5,x), min(x+5,len(corr)), y-min(5,y), min(y+5,len(corr[0])) )
    dat = np.copy(corr[fitbox[0]:fitbox[1],fitbox[2]:fitbox[3]])
    mback = corr.mean()
    para = fitgaussian2d(dat,mback)

    print fitbox
    print para

    correctx = fitbox[0]+para[2]-cutwindow
    correcty = fitbox[2]+para[3]-cutwindow

    print "Real position is {:} {:}".format(correctx,correcty)
    return correctx,correcty

def main():
    path = "/home/markus/LittleHelpers/LTOS/ExampleFiles/Green"
    images = readImageList(path)
    images = sorted(images)
    ref = 0
    drift = [[0,0,0]]
    imref = FIO.readImage(images[0])
    for i in xrange(1,len(images),1):
        print "Run {:}".format(i)
        compimage = FIO.readImage(images[i])
        x,y = correlateTwoImages(imref,compimage,100)
        drift.append([i,x+drift[ref][1],y+drift[ref][2]])
        if i % 10 == 0:
            ref = i
            imref = FIO.readImage(images[i])
    outf = open("saveDrift.txt",'w')
    outf.write("# Step xdrift ydrift")
    for line in drift:
        outf.write("{:} {:} {:}\n".format(line[0],line[1],line[2]))
    drift = np.transpose(drift)
    fig1, (ax1,ax2,ax3) = plt.subplots(3,1)
    ax1.plot(drift[0],drift[1],'-')
    ax2.plot(drift[0],drift[2],'-')
    ax3.plot(drift[1],drift[2],'-')
    plt.show()
    return
    
def testfunction():
    path = "/home/markus/LittleHelpers/LTOS/ExampleFiles/"
    image1 = np.array(FIO.readImage(path+"green0639.tif"))
    image3 = np.array(FIO.readImage(path+"green0001.tif"))
    correlateTwoImages(image1,image3,100)
    return

def readImageList(path):
    if not os.path.isdir(path):
        print "No path named " + path
        raise ValueError, "No path named " + path
    img = glob.glob(os.path.join(path, '*.tif'))
    print "Number of images found: " + str(len(img))
    return img


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
    #main()
    testfunction()
