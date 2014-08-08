'''===========================
===   Markus Rose          
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
    a = np.asarray(inImage.getdata())
#    print(a.dtype)
    a = np.resize(a.astype(float),inImage.size)
    return adjustRange(a)


'''
Image is not read as unsigned integer, so range is [-2^(bit/2),(2^(bit/2)-1)]
Range must be adjusted to [0,2^(bit)-1]
'''
def adjustRange(image):
    '''
    print(image.min())
    print
    '''
    for i in range(len(image)):
        for j in range(len(image[i])):
            if image[i,j] < 0:
                #print(j.min())
                image[i,j] = 65536 + image[i,j]
                #print(j.min())
    '''
    print
    print(image.min())
    '''
    return image


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


def detectParticle(img,sigma,local_max_window,signal_power,bit_depth,frame,eccentricity_thresh,sigma_thresh):
    image = readImage(img)
    saveImageToFile(image,"01sanityCheck.tif")

    gausFiltImage = ndimage.filters.gaussian_filter(image,sigma,order=0)
    saveImageToFile(gausFiltImage,"02gaussFilter.tif")
    
    localMaxImage = ndimage.filters.maximum_filter(gausFiltImage,size=local_max_window)
    saveImageToFile(localMaxImage,"03localMax.tif")

    img_max_filter = gausFiltImage.copy()
    img_max_filter[(gausFiltImage != localMaxImage)] = 0
    saveImageToFile(img_max_filter,"04MaxFilter.tif")
    
    median_img = ndimage.filters.median_filter(image, (21,21))
    saveImageToFile(median_img,"05MedianFilter.tif")
    (background_mean,background_std) = (median_img.mean(),median_img.std())
#    print(background_mean,background_std)

    imgMaxNoBack = (img_max_filter >= background_mean + signal_power * background_std)
    saveImageToFile(imgMaxNoBack,"05MaxFilter2.tif")
    if imgMaxNoBack.any() == True:
        print("JeaJeaJea")

#    gaussian_fit = pysm.new_cython.fit_gaussians_2d(image,sigma,
#            imgMaxNoBack,
#            background_mean,background_std,frame=0,template_size=None,
#            bit_depth=16,eccentricity_thresh=1.5,sigma_thresh=2)
    
#    if np.array_equal(img_max_filter,pysmMaxImage):
#        print("Jippiiiee")
#    else:
#        print("OhOh!!!")
    particle_list = []
    template_size = signal_power * np.ceil(sigma) - 1
    psf_range = np.floor(template_size/2)

    num_rows = image.shape[0]
    num_cols = image.shape[1]

    local_max_pixels = np.nonzero(imgMaxNoBack)
#    print np.transpose(local_max_pixels)

    print(len(local_max_pixels[0]))

    for i in xrange(len(local_max_pixels[0])):
        row0 = int(local_max_pixels[0][i])
        col0 = int(local_max_pixels[1][i])
        #print(row0,' ',col0)

        row_min = row0 - psf_range
        row_max = row0 + psf_range
        col_min = col0 - psf_range
        col_max = col0 + psf_range

        if (row_min < 0 or row_max >= num_rows or
                col_min < 0 or col_max >= num_cols):
            print("Oh, too close to frame boarder to fit a gaussian.")
            continue
        else:
            print("So where is the point?")

        
        ''' #Check ROI 
        print("row0 = ",row0)
        print("col0 = ",col0)
        print("row_min = ",row_min)
        print("row_max = ",row_max)
        print("col_min = ",col_min)
        print("col_max = ",col_max)
        '''

        fitdata = pysm.new_cython.fitgaussian2d(
                    image[row_min:row_max, col_min:col_max],
                    background_mean)
        
        print(fitdata)


        ##############
        #FIT CHECKING
        ##############
        if fitdata[0] <= 0 or fitdata[1] <=0:
            #Fit did not converge
            continue
        
        if (np.abs(fitdata[5]/fitdata[4]) >= eccentricity_thresh or 
            np.abs(fitdata[4]/fitdata[5]) >= eccentricity_thresh):
            #Fit too eccentric
            continue
        
        if (fitdata[4] > (sigma_thresh * sigma) or 
			fitdata[4] < (sigma / sigma_thresh) or
            fitdata[5] > (sigma_thresh * sigma) or
            fitdata[5] < (sigma / sigma_thresh)):
            #Fit too unlike theoretical psf
            continue

        
        #Create a new Particle
        #TODO:        
        #p = cparticle.CParticle()
        p = pysm.new_cython.TempParticle()        
        
        #TODO: Implement Particle ID
        p.frame = frame
        p.position = np.array([row_min, row_max, col_min, col_max])
        
        p.height = fitdata[0]
        p.amplitude = fitdata[1]
        
        #TODO: FIX THIS BUG (switching of x and y)
        p.y = fitdata[2] + row_min
        p.x = fitdata[3] + col_min
        p.width_x = np.abs(fitdata[4])
        p.width_y = np.abs(fitdata[5])
        p.volume = (2 * np.pi * p.amplitude * p.width_x * p.width_y)
        
        # normalized volume for intensity moment descrimination in
        # linking step
        p.norm_volume = \
        	(2 * np.pi * (p.amplitude / (2**bit_depth - 1)) * 
			 p.width_x * p.width_y)
        
        # calculate signal to noise
        # (for our purposes a simple calc of amplitude of signal minus 
        # the background over the intensity of the background)
        p.sn = (p.amplitude + p.height) / p.height
        
        particle_list.append(p)
    print(len(particle_list))

    return particle_list

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
    detectParticlePosition("tester.tif","outTest.tif",determineCutoff)
    #detectParticlePosition("tester.tif","otsuTest.tif",otsuMethod)


