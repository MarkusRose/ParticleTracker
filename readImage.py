'''===========================
===   Markus Rose          ===
==========================='''

from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import pysm.thresholding
import pysm.new_cython
from scipy import ndimage
from scipy.misc import imsave


'''First we have to read the image'''
def readImage(imagepath):
    inImage = Image.open(imagepath)
    print inImage
    bit_depth = 16
    if inImage.mode == 'L':
        bit_depth = 8
    elif inImage.mode == 'I;16B':
        bit_depth = 16
    else:
        print("Bit_depth unknown, set to 16bit")
        bit_depth = 16

    a = np.asarray(inImage.getdata())
#    print(a.dtype)
    a = np.resize(a.astype(float),inImage.size)
    print a.shape
    print bit_depth
    return adjustRange(a,bit_depth)


'''
Image is not read as unsigned integer, so range is [-2^(bit/2),(2^(bit/2)-1)]
Range must be adjusted to [0,2^(bit)-1]
'''
def adjustRange(image,bit_depth):
    '''
    print(image.min())
    print
    '''
    for i in xrange(len(image)):
        for j in xrange(len(image[i])):
            if image[i,j] < 0:
                #print(image.min())
                image[i,j] = 65536 + image[i,j]
                #print(image.min())
    '''
    print
    print(image.min())
    '''
    return image/(1.0*(2**bit_depth))


'''
Determine a Cutoff at mean of maximum and minimum intensity
'''
def determineCutoff(image):
    imageMax = image.max()
    imageMin = image.min()
    hist = np.histogram(image,bins=100)
    sumhist = hist[0].cumsum()
    for i in range(len(hist[1])):
        if hist[1][i] > (imageMax+imageMin)/2:
            break
    #return (hist[1][i],imageMax,sumhist[i],image.size)
    return hist[1][i]


'''
Determine cutoff via the Otsu Method
'''
def otsuMethod(image):
    return pysm.thresholding.otsu(image,16)


'''
Use a cutoff method on image array
'''
def cutImage(image,cutoffMethod):
    cutoff = cutoffMethod(image)
    newImage = np.ndarray(image.shape)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            '''
            if image[i][j] < 0:
                newImage[i][j] = image.max()
            '''
            if image[i][j] < cutoff:
                newImage[i][j] = 0
            else:
                newImage[i][j] = image.max()
    return newImage

def saveImageToFile(inArray,outName):
    #print inArray.dtype
    imsave(outName,inArray)

'''--------------------
--  Testing methods  --
--------------------'''
def detectParticlePosition(inImage,outImage,cutoffMethod):
    image = readImage(inImage)
    cutI = cutImage(image,cutoffMethod)
    #outI = Image.fromarray(cutI.astype("uint16"),'I;16B')
    #outI.save(outImage)
    cutI2 = pysm.new_cython.gaussian_filter_image(image,1.0)
    outI = Image.fromarray(cutI2.astype("uint16"),'I;16B')
    outI.save("gaussfit-"+outImage)
    cutI3 = pysm.new_cython.local_maximum(cutI2)
    outI = Image.fromarray(cutI3.astype("uint16"),'I;16B')
    outI.save("localmax-"+outImage)

    median_img = ndimage.median_filter(image,(21,21))
    outI = Image.fromarray(median_img.astype("uint16"),'I;16B')
    outI.save("median-"+outImage)

    (background_mean, background_std) = pysm.new_cython.estimate_background_median(image,(21,21))
    print background_mean, background_std


    listOfParticles = []
#    listOfParticles = pysm.new_cython.detect_particles_deflation(cutI)
    print(listOfParticles)


if __name__=="__main__":
    detectParticlePosition("/data/NEHADexperiments/2013-08-14/mito_DiD_Images/mito_DiD0000.tif","outTest.tif",determineCutoff)
    #detectParticlePosition("tester.tif","otsuTest.tif",otsuMethod)


