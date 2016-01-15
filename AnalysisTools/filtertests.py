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
        outf.write("{:} {:} {:} {:} {:}\n".format(float(image.max()),float(image.min()),image.mean(),image.std(), (float(image.max())-image.mean())/image.std()))
        return
    
    
    outf.write("# Signal to noise {:}\n".format(int(signoise)))
    outf.write("# Original, Median, Boxcar, Gaussian, Binary\n")
    outf.write("# MAX    MIN      MEAN     STD     SNR\n")
    data = readImage("frame"+filename+".tif")

    if output:
        saveImageToFile(data,"Original"+filename+".png")
    #print
    #print "Original Image"
    #print data.max(), data.min(), data.mean(), data.std()
    #print
    writeline(data)

    median = ndimage.filters.median_filter(data, (21,21))

    #print
    #print "Median Image"
    #print median.max(), median.min(), median.mean(), median.std()
    #print
    writeline(median)

    if output:
        saveImageToFile(median,"median"+filename+".png")

    (background_mean,background_std) = (median.mean(),median.std())
    #print background_mean, background_std
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std
    if cutoff == 0:
        #print "Cutoff is {}: ".format(cutoff)
        cutoff = 1e-10
        #print "setting cutoff to {}".format(cutoff)

    boxcar = Detection.filters.boxcarFilter(data,boxsize=5,cutoff=cutoff)

    #print
    #print "Boxcar Image"
    #print boxcar.max(),boxcar.min(),boxcar.mean(),boxcar.std()
    #print
    writeline(boxcar)

    if output:
        saveImageToFile(boxcar,"boxFilter"+filename+".png")

    gaussian = ndimage.filters.gaussian_filter(boxcar,2,order=0)

    #print
    #print "Gaussian Image"
    #print gaussian.max(), gaussian.min(), gaussian.mean(), gaussian.std()
    #print 
    writeline(gaussian)

    if output:
        saveImageToFile(gaussian,"gauss"+filename+".png")

    (background_mean,background_std) = (gaussian.mean(),gaussian.std())
    ##print background_mean, background_std
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std

    binary = (gaussian >= cutoff)

    #print                       # 
    #print "Binary Image"
    #print binary.max(), binary.min(), binary.mean(), binary.std()
    #print
    writeline(binary)

    if output:
       saveImageToFile(binary,"BinaryFilter2{0:03d}.png".format(int(signoise)))

    #print
    #print "Cutoff generated"
    #print cutoff, background_mean, signal_power, background_std
    #print
    
    return



def mainTestSimulation():
    
    os.mkdir("FilterBenchmark")
    os.chdir("FilterBenchmark")

    

    background = 10000
    backnoise = 100
    intensity = 4
    
    intcount = 0
    
    for intensity in [4,400,40000]:
        intback = 0
        for background in [0,100,10000]:
            fileout = open("ImageMoments{0:1d}{1:1d}.txt".format(intcount,intback),'w')
            os.mkdir("I{0:}-B{1:}".format(intensity,background))
            os.chdir("I{0:}-B{1:}".format(intensity,background))
            print "{0:1d}{1:1d}".format(intcount,intback)
            for backnoise in [4,2,1.33,1,0.80,0.66,0.57,0.50,0.40,0.20,0.10]:
                if intcount == 1:
                    backnoise *= 100
                elif intcount == 2:
                    backnoise *= 10000

                signoise = intensity*1.0/backnoise
                print "    {0:02d}".format(int(signoise))

                fileout.write("# background = {:}\n".format(background))
                fileout.write("# background noise = {:}\n".format(backnoise))
                fileout.write("# intensity = {:}\n".format(intensity))

                makeImage([[1,34.4,34.4,0,0,intensity]],intcount*1000+intback*100+int(signoise),".",512,0.16,(0.5*0.7/1.45/0.16)**2,background,backnoise)
                #print (intcount*1000+intback*100+int(signoise))
                #print "{0:02d}".format(int(signoise))
                #print "{0:1d}{1:1d}{2:02d}".format(intcount,intback,int(signoise))
                analyseImage("{0:1d}{1:1d}{2:02d}".format(intcount,intback,int(signoise)),fileout,signoise)
                fileout.write("\n\n")
            intback += 1
            fileout.close()
            os.chdir("../")
        intcount += 1
    return


def realData():
    
    os.mkdir("RealData")
    os.chdir("RealData")

    fileout = open("ImageMomentsReal.txt",'w')
    analyseImage("0010",fileout,
        

if __name__=="__main__":
    mainTest()
