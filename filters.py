import readImage
import matplotlib.pyplot as plt
import numpy as np
import markPosition as mark


def boxcarFilter(image,boxsize=3,cutoff=1.0):
    halfsize = boxsize/2
    changed = np.zeros(image.shape)
    for i in xrange(len(image)):
        for j in xrange(len(image[i])):
            sum = 0
            counter = 0
            #if image[i,j] > cutoff:
            #    changed[i,j] = image[i,j]
            #    print("Pixel brighter than cutoff: " + str((i,j)))
            #    continue
            for k in xrange(boxsize):
                ksaver = i+k-halfsize
                if ksaver < 0 or ksaver >= len(image):
                    continue
                for l in xrange(boxsize):
                    lsaver = j+k-halfsize
                    if lsaver < 0 or lsaver >= len(image[i]):
                        continue
                    counter += 1
                    if image[ksaver,lsaver] > cutoff:
                        sum += cutoff
                    else:
                        sum += image[ksaver,lsaver]
            sum /= counter
            if image[i,j] > sum:
                changed[i,j] = image[i,j] - sum
            else:
                changed[i,j] = 0
    return changed

if __name__=="__main__":
    image = readImage.readImage("images/tester.tif")
    boxsize = 20
    cutoff = 1.0

    changed = boxcarFilter(image,boxsize,cutoff)

    plt.imshow(changed,cmap=plt.cm.gray)
    plt.show()

    #mark.saveRGBImage(mark.convertRGB(image),"original.tif")
    mark.saveRGBImage(mark.convertRGB(changed),"boxcartest.tif")

    print("done")
