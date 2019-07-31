import numpy as np
import matplotlib.pyplot as plt
import skimage.io as io


def centroidMethod(gausFiltImage,cutoff):
    binaryMap = (gausFiltImage > (cutoff))
    clusterImage = - binaryMap.astype(int)

    def checkNN(i,j,clco):
        if i > 0 and clusterImage[i-1,j] == -1:
            clusterImage[i-1,j] = clco
            toDo.append([i-1,j])
        if i < len(clusterImage)-1 and clusterImage[i+1][j] == -1:
            clusterImage[i+1,j] = clco
            toDo.append([i+1,j])
        if j > 0 and clusterImage[i,j-1] == -1:
            clusterImage[i,j-1] = clco
            toDo.append([i,j-1])
        if j < len(clusterImage[0])-1 and clusterImage[i,j+1]:
            clusterImage[i,j+1] = clco
            toDo.append([i,j+1])
    
    toDo = []
    clco = 0
    countnet1 = 0
    clusters = []
    for i in range(len(clusterImage)):
        for j in range(len(clusterImage[i])):
            if clusterImage[i,j] == 0:
                continue
            elif clusterImage[i,j] == -1:
                countnet1 += 1
                #print i,j
                clco += 1
                clusters.append([])
                clusterImage[i,j] = clco
                toDo.append([i,j])
                while len(toDo) > 0:
                    checkNN(toDo[0][0],toDo[0][1],clco)
                    clusters[clco-1].append(toDo[0])
                    del toDo[0]
    #print "done clustering"
    #print countnet1
    local_max_pixels = [[],[]]
    #sizecheck = []
    i = 0
    while i < len(clusters):
        if len(clusters[i]) < 5:
            clusters.pop(i)
            continue
        else:
            #sizecheck.append(len(clusters[i]))
            i += 1
    #print("\nNumber of clusters after restrict: " + str(len(clusters)))
    #print("Cluster size: " + str(np.array(sizecheck).mean()) + " +- " + str(np.array(sizecheck).std()) + "\n")

    for clust in clusters:
        #calculate centroid for each cluster and append
        x = 0
        y = 0
        sizeOC = 0
        for part in clust:
            sizeOC += 1
            x += part[0]
            y += part[1]
        local_max_pixels[0].append((1.0*x)/sizeOC)
        local_max_pixels[1].append((1.0*y)/sizeOC)
    #print "done getting local maxs"
    #print local_max_pixels
    return local_max_pixels[0][0],local_max_pixels[1][0]


