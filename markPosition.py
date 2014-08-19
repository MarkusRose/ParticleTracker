import numpy as np
from scipy.misc import imsave

def treasure(size_x,size_y,thickness):
    a = np.zeros((size_x,size_y))
    i,j = 0,0

    for i in range(len(a)):
        for j in range(len(a[i])):
            if (j <= i + thickness and j >= i - thickness) or (j <= len(a) - i - 1
                    + thickness and j >= len(a) - i - 1 - thickness):
                a[i,j] = 1
    return a

def placeWidget(image,pos_x,pos_y):
    widget = treasure(7,7,0)
    center = int(widget.shape[0]/2)

    for i in xrange(len(widget)):
        for j in xrange(len(widget[i])):
            if pos_x + i - center > -1 and pos_y + j  - center > -1 and pos_x+i-center < len(image) and pos_y+j-center < len(image[pos_x+i-center]):
                #print((pos_x,pos_y),(i,j))
                if widget[i,j] != 0:
                    image[pos_x - center + i,pos_y - center + j] = widget[i,j]*image.max()

    return image

def markPositionsFromList(image,posList):
    for i in posList:
        placeWidget(image,i.y,i.x)
    imsave('markedPos.tif',image)

def makeRegularImage():
    image = np.zeros((512,512))


#    for i in xrange(512):
#        for j in xrange(512):
#            if (i*j)%100 == 0:
#                placeWidget(image,i,j)

    for i in range(512):
        for j in range(512):
            if i%30 ==0 and j%30 == 0:
                placeWidget(image,i,j)

    imsave('helloX.tif',image)

    return image


    
