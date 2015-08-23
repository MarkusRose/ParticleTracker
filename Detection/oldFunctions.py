

def giveInitialFitting(image,tracks,signal_power,sigma,sigma_thresh,eccentricity_thresh,bit_depth,oname):
    print "Start with initial position given"
    partlist = []
    for part in tracks:
        median_img = ndimage.filters.median_filter(image, (21,21))
        (background_mean,background_std) = (median_img.mean(),median_img.std())
        isIt = determineFittingROI(image.shape,part[1],part[2],signal_power,sigma)
        if isIt:
            rmin,rmax,cmin,cmax = isIt
        else:
            print("Missed frame {:}".format(part[0]))
            continue

        fitdata = fitgaussian2d(image[rmin:rmax,cmin:cmax],background_mean)
        
        checkedfit = checkFit(fitdata,sigma,sigma_thresh,eccentricity_thresh,0,0,0)
        if not checkedfit[0]:
            print("Fit does not fit!")
            continue
        
        addParticleToList(partlist,(part[0]/0.16),rmin,rmax,cmin,cmax,fitdata)

    outfile = open(oname,'w')
    outfile.write("# frame x y \n")
    for p in partlist:
        outfile.write("{:} {:} {:}\n".format(p.frame,p.x,p.y))
    outfile.close()
    print "end with initial pos"
    return partlist


        
def printPictures(tracks,numtrack):
    position = pysm.new_cython.TempParticle()
    for i in xrange(1,40):
        print("# {:} =====================".format(i))
        image = readImage.readImage(img[i-1])
        position.x= tracks[numtrack-1].track[i]['x']
        position.y= tracks[numtrack-1].track[i]['y']
        markings = markPosition.markPositionsFromList(image.shape,[position])
        markedlines = markPosition.connectPositions(image.shape,tracks[numtrack-1].track[1:i+1])
        markPosition.justsuper(image,markings,markedlines,"marked"+str(i)+".tif")
        #markPosition.superimpose(image,markings,"marked"+str(i)+".tif")
        print ""

def testTracks(tracks):        
    print("Done creating tracks")
    print('ChooChoo! Track 29: \n' + str(tracks[29].track))
    print("Boy, you can give me a schein")
    for name in tracks[29].track.dtype.names:
        print(name + ": " + str(tracks[29].track[name]))
    return   

def compareInitNoInit(image,data,out):

    initPos = convertFiles.convImageJTrack(data)
    markInit = markPosition.markPositionsSimpleList(image.shape,initPos)
    
    partdata = detectParticles.giveInitialFitting(image,initPos,signal_power,sigma,sigma_thresh,eccentricity_thresh,bit_depth,"out.txt")
    markWithInit = markPosition.markPositionsFromList(image.shape,partdata)

    partdata = detectParticles.detectParticles(image,sigma,local_max_window,signal_power,bit_depth,0,eccentricity_thresh,sigma_thresh,True)
    markNoInit = markPosition.markPositionsFromList(image.shape,partdata[0])
    markFromNoInit = markPosition.markPositionsSimpleList(image.shape,readLocalMax("foundLocalMaxima.txt"))
    boxMarkings = markPosition.drawBox(image.shape,readBox("localBoxes.txt"))
    

    ofile = open("simNoInit.txt",'w')
    detectParticles.writeDetectedParticles(partdata,1,ofile)


    outar = markPosition.autoScale(markPosition.convertRGBGrey(image))
    #outar = markPosition.imposeWithColor(outar,markInit,'B')
    #outar = markPosition.imposeWithColor(outar,markFromNoInit,'G')
    outar = markPosition.imposeWithColor(outar,markNoInit,'R')
    outar = markPosition.imposeWithColor(outar,boxMarkings,'G')

    markPosition.saveRGBImage(outar,out)
    return


def lotsOfTrials():

    readConfig("setup.txt")

    image = readImage.readImage("simData.tif")
    signal_power = 14
    compareInitNoInit(image,"simResults.txt","simOut.tif")



    image = readImage.readImage("singleData1.tif")
    markPosition.saveRGBImage(markPosition.autoScale(image),"singleOData1scaled.tif")
    signal_power = 5
    compareInitNoInit(image,"singleResults1.txt","singleOut.tif")
    image += readImage.readImage("singleData2.tif")
    image += readImage.readImage("singleData3.tif")
    markPosition.saveRGBImage(markPosition.autoScale(image),"addedOData1scaled.tif")
    compareInitNoInit(image,"singleResults1.txt","addedOut.tif")



    #particle_data = makeDetectionFromFile()

    #makeTracks(particle_data)
    
    #tracks = convertFiles.convImageJTrack("/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/VisTrack01.xls")

    '''
    image = readImage.readImage(img[tracks[0][0]-1])
    print(tracks[0][0])
    print(tracks[0][1],tracks[0][2])
    print(image[tracks[0][1],tracks[0][2]])
    '''
    #oname = "/data/AnalysisTracks/2014-10-26_Mito-Lipid_Tracks/Mito_DiD001-2-HandTracks/newTrack02.txt"
    #detectParticles.giveInitialFitting(img,tracks,signal_power,sigma,sigma_thresh,eccentricity_thresh,bit_depth,oname)
    
    print("\nDone!\n---------\n")
    return
