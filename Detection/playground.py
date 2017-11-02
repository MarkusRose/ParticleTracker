from . import readImage

window = 10


def readXYValue(img, xxx_todo_changeme):
    (x,y) = xxx_todo_changeme
    image = readImage.readImage(img)

    #read Value from Array
    if x < len(image) and y < len(image[x]) and x > -1 and y > -1:
        v = image[x,y]
    else:
        raise Exception("X or Y out of bounds")
    #return Value
    return v

def readRow(img,x):
    image = readImage.readImage(img)

    if x < len(image) and x > -1:
        v = image[x]
    else:
        raise Exception("X out of bounds")
    return v

def readColumn(img,y):
    image = readImage.readImage(img)
    image = image.transpose()
    if y < len(image) and y > -1:
        v = image[y]
    else:
        raise Exception("Y out of bounds")
    return v

def writeOutput(img,pos,outfile):
    xexp = window
    yexp = window
    out = open(outfile,'w')
    image = readImage.readImage(img)

    if pos[0] >=len(image) or pos[1] >= len(image[0]) or pos[0] < 0 or pos[1] < 0:
        raise Exception("PROOOBLEM")
    if pos[0] + xexp >= len(image):
        xexp = len(image)-pos[0]
    if pos[1] + yexp >= len(image[0]):
        yexp = len(image[0])-pos[1]
    if pos[0] - xexp < 0:
        xexp = pos[0]
    if pos[1] - yexp < 0 :
        yexp = pos[1]

    out.write("# Pixelx Pixely Value\n")
    for i in range(xexp*2+1):
        for j in range(yexp*2+1):
            a = pos[0]-xexp+i
            b = pos[1]-yexp+j
            out.write("{:} {:} {:}\n".format(a,b,image[a,b]))
    out.close()
    return

    
if __name__=="__main__":
    path = "../SmallMito/mitoW0051.tif"
    writeOutput(path,(52,83),"outputmenow.txt")
