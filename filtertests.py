import numpy as np
import Detection.filters
from scipy import ndimage
import os

from Detection.readImage import readImage,saveImageToFile
from System.Fileio import makeImage

output = True
signal_power = 5


def analyseImage(filename,outf,signoise):
        
    def writeline(image):
        outf.write("{:} {:} {:} {:}\n".format(float(image.max()),float(image.min()),image.mean(),image.std(), (float(image.max())-image.mean())/image.std()))
        return
    
    
    outf.write("# Signal to noise {:}\n".format(int(signoise*10)))
    outf.write("# Original, Median, Boxcar, Gaussian, Binary\n")
    outf.write("# MAX    MIN      MEAN     STD     SNR\n")
    data = readImage(filename)

    if output:
        saveImageToFile(data,"20OriginalImage2{0:03d}.png".format(int(signoise*10)))
    print
    print "Original Image"
    print data.max(), data.min(), data.mean(), data.std()
    print
    writeline(data)

    median = ndimage.filters.median_filter(data, (21,21))

    print
    print "Median Image"
    print median.max(), median.min(), median.mean(), median.std()
    print
    writeline(median)

    if output:
        saveImageToFile(median,"21medianFilter2{0:03d}.png".format(int(signoise*10)))

    (background_mean,background_std) = (median.mean(),median.std())
    #print background_mean, background_std
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std
    if cutoff == 0:
        #print "Cutoff is {}: ".format(cutoff)
        cutoff = 1e-10
        #print "setting cutoff to {}".format(cutoff)

    boxcar = Detection.filters.boxcarFilter(data,boxsize=5,cutoff=cutoff)

    print
    print "Boxcar Image"
    print boxcar.max(),boxcar.min(),boxcar.mean(),boxcar.std()
    print
    writeline(boxcar)

    if output:
        saveImageToFile(boxcar,"22boxFilter2{0:03d}.png".format(int(signoise*10)))

    gaussian = ndimage.filters.gaussian_filter(boxcar,2,order=0)

    print
    print "Gaussian Image"
    print gaussian.max(), gaussian.min(), gaussian.mean(), gaussian.std()
    print 
    writeline(gaussian)

    if output:
        saveImageToFile(gaussian,"23gaussFilter2{0:03d}.png".format(int(signoise*10)))

    (background_mean,background_std) = (gaussian.mean(),gaussian.std())
    #print background_mean, background_std
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std

    binary = (gaussian >= cutoff)

    print
    print "Binary Image"
    print binary.max(), binary.min(), binary.mean(), binary.std()
    print
    writeline(binary)

    if output:
       saveImageToFile(binary,"24BinaryFilter2{0:03d}.png".format(int(signoise*10)))

    print
    print "Cutoff generated"
    print cutoff, background_mean, signal_power, background_std
    print
    
    return



if __name__=="__main__":
    
    #os.mkdir("FilterBenchmark")
    os.chdir("FilterBenchmark")

    
    fileout = open("ImageMoments2.txt",'w')

    background = 10000
    backnoise = 100
    intensity = 4
    
    for backnoise in [4,2,1.33,1,0.80,0.66,0.57,0.50,0.40,0.20,0.10]:
        #backnoise *= 100
        signoise = intensity*1.0/backnoise

        fileout.write("# background = {:}\n".format(background))
        fileout.write("# background noise = {:}\n".format(backnoise))
        fileout.write("# intensity = {:}\n".format(intensity))

        makeImage([[1,34.4,34.4,0,0,intensity]],2000+int(signoise*10),".",512,0.16,(0.5*0.7/1.45/0.16)**2,background,backnoise)
        analyseImage("frame2{0:03d}.tif".format(int(signoise*10)),fileout,signoise)
        fileout.write("\n\n")
