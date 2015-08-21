import Image
import numpy

data = numpy.zeros((1024,1024),numpy.uint16)

h,w = data.shape

for i in range(h):
    data[i,:] = numpy.arange(w)

im = Image.fromstring('I;16',(w,h),data.tostring())
im.save('test_16bit.tif')
