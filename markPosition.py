import numpy as np
from scipy.misc import imsave
from PIL import Image

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
    #posImage = np.zeros(image.shape)
    #print(image.shape)
    widget = treasure(7,7,0)
    center = int(widget.shape[0]/2)

    for i in xrange(len(widget)):
        for j in xrange(len(widget[i])):
            if pos_x + i - center > -1 and pos_y + j  - center > -1 and pos_x+i-center < len(image) and pos_y+j-center < len(image[pos_x+i-center]):
                #print((pos_x,pos_y),(i,j))
                if widget[i,j] != 0:
                    image[pos_x - center + i,pos_y - center + j] = widget[i,j]

    return image

def drawLine(one_x,one_y,two_x,two_y):
    image = np.zeros((int(abs(two_x - one_x))+1,int(abs(two_y - one_y))+1))

    if two_y == one_y:
        image[:] = 1
    elif one_x == two_x:
        image[:] = 1
    else:
        for y in xrange(1,image.shape[1]):
            x = (two_x-one_x)*y/(two_y-one_y)
            if two_y-one_y < 0:
                y = 0 - y
                x = 0 - x
            if x < 0:
                x = 0 - x
            image[int(x),y] = 1
        #TODO:place remaining starting points
        #image[min(one,0] = 1
        #image[image.shape[0]-1,image.shape[1]-1] = 1
    return image

def placeImage(bild,img,x,y):
    for i in xrange(len(img)):
        for j in xrange(len(img[i])):
            if img[i,j] != 0:
                bild[x+i,y+j] = img[i,j]
    return bild

def placeLine(image,one_x,one_y,two_x,two_y):
    widget = drawLine(one_x,one_y,two_x,two_y)
    image = placeImage(image,widget,min(one_x,two_x),min(one_y,two_y))
    return image


def markPositionsFromList(image,posList):
    markings = np.zeros(image.shape)
    for i in posList:
        placeWidget(markings,i.y,i.x)
    return markings

def connectPositions(image,posList):
    markings = np.zeros(image.shape)
    for i in xrange(len(posList)-1):
        print(str((posList[i].x, posList[i].y)) + " -> " + str((posList[i+1].x,posList[i+1].y)))
        markings = placeLine(markings,posList[i].y,posList[i].x,posList[i+1].y,posList[i+1].x)
    return markings
        

def superconnected(image,markings):
    image = image * ((2**8) - 1)
    markings = markings * ((2**8)-1)
    image = image.astype(np.uint8)
    markings = markings.astype(np.uint8)

    data = np.zeros((image.shape[0],image.shape[1],3))
    data[:,:,0] = image 
    data[:,:,1] = image 
    data[:,:,2] = image 

    for i in range(len(data)):
        for j in range(len(data[i])):
            if markings[i,j] != 0:
                data[i,j] = [0,0,255]
    
    data = data.astype(np.uint8)
    img = Image.fromarray(data, 'RGB')
    img.save('myconn.tif')

    return

def justsuper(image,markings,markedlines):
    image = image * ((2**8) - 1)
    markings = markings * ((2**8)-1)
    markedlines = markedlines * ((2**8)-1)
    image = image.astype(np.uint8)
    markings = markings.astype(np.uint8)
    markedlines = markedlines.astype(np.uint8)

    data = np.zeros((image.shape[0],image.shape[1],3))
    data[:,:,0] = image 
    data[:,:,1] = image 
    data[:,:,2] = image 

    for i in range(len(data)):
        for j in range(len(data[i])):
            if markings[i,j] != 0:
                data[i,j] = [255,0,0]
            if markedlines[i,j] != 0:
                data[i,j] = [0,0,255]
            
    data = data.astype(np.uint8)
    img = Image.fromarray(data, 'RGB')
    img.save('my.tif')

    return


def superimpose(image,markings):
    image = image * ((2**8) - 1)
    markings = markings * ((2**8)-1)
    image = image.astype(np.uint8)
    markings = markings.astype(np.uint8)

    data = np.zeros((image.shape[0],image.shape[1],3))
    data[:,:,0] = image 
    data[:,:,1] = image 
    data[:,:,2] = image 

    for i in range(len(data)):
        for j in range(len(data[i])):
            if markings[i,j] != 0:
                data[i,j] = [255,0,0]
    
    data = data.astype(np.uint8)
    img = Image.fromarray(data, 'RGB')
    img.save('mypos.tif')

    return

def makeRegularImage():
    image = np.zeros((512,512))
    for i in xrange(512):
        for j in xrange(512):
            if i%30 ==0 and j%30 == 0:
                placeWidget(image,i,j)
    imsave('helloX.tif',image)
    return image


    
