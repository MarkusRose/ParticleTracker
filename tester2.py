import Image
import numpy
from libtiff import TIFFimage

data = numpy.zeros((1024,1024),numpy.uint16)

h,w = data.shape

for i in range(w):
    data[:,i] = numpy.arange(h)

tiff = TIFFimage(data, description='')
tiff.write_file('test_16bit.tif', compression='lzw')
#flush the file to disk:
del tiff
