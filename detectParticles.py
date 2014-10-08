import numpy as np
import pysm.new_cython
import readImage
import filters
from scipy import ndimage, optimize


def writeDetectedParticles(particles):
    outfile = open("foundParticles.txt",'w')
    for i in range(len(particles)):
        outfile.write('\n#-Frame {:2.0f} -------------------------------------\n'.format(i+1))
        outfile.write('# Number of particles: ' + str(len(particles[i][0])) + '\n')
        outfile.write('# Cutoff value used: {:.1f} \n'.format(particles[i][1]))
        outfile.write("# x       y        width_x      width_y   height  amplitude  sn  volume \n")
        for p in particles[i][0]:
            outfile.write('{:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} \n'.format(p.x,p.y,p.width_x,p.width_y,p.height,p.amplitude,p.sn,p.volume))
    return

def multiImageDetect(img,
                    sigma,
                    local_max_window,
                    signal_power,
                    bit_depth,
                    eccentricity_thresh,
                    sigma_thresh,output=False):
    particle_data = []
    frame = 0
    for image in img:
        frame += 1
        print("\n==== Doing image no " + str(frame) + " ====")
        particles = detectParticles(
                image,
                sigma,
                local_max_window,
                signal_power,
                bit_depth,
                frame,
                eccentricity_thresh,
                sigma_thresh,output)

        particle_data.append(particles)
    writeDetectedParticles(particle_data)
    pd = []
    for fr in particle_data:
        pd.append(fr[0])
#    print pd
    return pd

def fitgaussian2d(data, background_mean, user_moments = None):
    """Returns (height, amplitude, x, y, width_x, width_y) as a numpy array
    found by least squares fitting of gaussian variables:"""
    
    if user_moments == None:
        initial_params = image_moments(data, background_mean)
    else:
        initial_params = user_moments
    
    #ravel is a special case for "unraveling" higher dimensional arrays into 1D arrays
    errorfunction = lambda p: np.ravel((gaussian2d(*p)(*np.indices(data.shape)) - data))
    p, cov, infodict, errmsg, success = optimize.leastsq(errorfunction, initial_params, full_output=1)
    return p

def image_moments(data, mean_background):
    total = data.sum()
    Y,X = np.indices(data.shape)
  
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    
    col = data[:, int(x)]
    width_y = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    
    row = data[int(y), :]
    width_x = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    
    height = mean_background
    amplitude = data.max() - height
    
    return (height, amplitude, x, y, width_x, width_y)

def gaussian2d(height, amplitude, center_x, 
               center_y, width_x, width_y):
    """Return 2d gaussian lamda(x,y) function"""
    
    height = float(height)
    amplitude = float(amplitude)
    width_x = float(width_x)
    width_y = float(width_y)
    
    return (lambda x,y: height + 
            amplitude*np.exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2))

def detectParticles(img,sigma,local_max_window,signal_power,bit_depth,frame,eccentricity_thresh,sigma_thresh,output):
    image = readImage.readImage(img)
    if output:
        readImage.saveImageToFile(image,"01sanityCheck.tif")

    median_img = ndimage.filters.median_filter(image, (21,21))
    if False:
        readImage.saveImageToFile(median_img,"05MedianFilter1.tif")
    (background_mean,background_std) = (median_img.mean(),median_img.std())
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std

    boxcarImage = filters.boxcarFilter(image,boxsize=5,cutoff=cutoff)
    if output:
        readImage.saveImageToFile(boxcarImage,"02boxFilter.tif")

    gausFiltImage = ndimage.filters.gaussian_filter(boxcarImage,sigma,order=0)
    if output:
        readImage.saveImageToFile(gausFiltImage,"02gaussFilter.tif")
    
    localMaxImage = ndimage.filters.maximum_filter(gausFiltImage,size=local_max_window)
    if output:
        readImage.saveImageToFile(localMaxImage,"03localMax.tif")

    img_max_filter = gausFiltImage.copy()
    img_max_filter[(gausFiltImage != localMaxImage)] = 0
    if output:
        readImage.saveImageToFile(img_max_filter,"04MaxFilter.tif")
    
    print("Cutoff is at: {:}".format(cutoff))
    median_img = ndimage.filters.median_filter(gausFiltImage, (21,21))
    if False:
        readImage.saveImageToFile(median_img,"05MedianFilter2.tif")
    (background_mean,background_std) = (median_img.mean(),median_img.std())
    #cutoff = readImage.otsuMethod(image)
    cutoff = background_mean + signal_power * background_std

    print("Cutoff is at: {:}".format(cutoff))
    print("Max of MaxFilter is at: {:}".format(img_max_filter.max()))
    imgMaxNoBack = (img_max_filter >= cutoff)
    if output:
        readImage.saveImageToFile(imgMaxNoBack,"05MaxBinary.tif")
     #Check if maxima found
    if imgMaxNoBack.any() == True:
        print("JeaJeaJea")
    else:
        print("NoNoNo")

#    gaussian_fit = pysm.new_cython.fit_gaussians_2d(image,sigma,
#            imgMaxNoBack,
#            background_mean,background_std,frame=0,template_size=None,
#            bit_depth=16,eccentricity_thresh=1.5,sigma_thresh=2)
    
#    if np.array_equal(img_max_filter,pysmMaxImage):
#        print("Jippiiiee")
#    else:
#        print("OhOh!!!")
    particle_list = []
    template_size = signal_power * np.ceil(sigma) - 1
    psf_range = np.floor(template_size/2)

    num_rows = image.shape[0]
    num_cols = image.shape[1]

    local_max_pixels = np.nonzero(imgMaxNoBack)
    #print np.transpose(local_max_pixels)

    print('Cutoff is at ' + str(cutoff))
    print("Found local Maxima: "+str(len(local_max_pixels[0])))

    for i in xrange(len(local_max_pixels[0])):
        row0 = int(local_max_pixels[0][i])
        col0 = int(local_max_pixels[1][i])
        #print(row0,' ',col0)

        row_min = row0 - psf_range
        row_max = row0 + psf_range
        col_min = col0 - psf_range
        col_max = col0 + psf_range

        if (row_min < 0 or row_max >= num_rows or
                col_min < 0 or col_max >= num_cols):
            #print("Oh, too close to frame boarder to fit a gaussian.")
            continue
        else:
            #print("So where is the point?")
            pass

        
        '''
        #Check ROI 
        print("row0 = ",row0)
        print("col0 = ",col0)
        print("row_min = ",row_min)
        print("row_max = ",row_max)
        print("col_min = ",col_min)
        print("col_max = ",col_max)
        '''

        fitdata = fitgaussian2d(
                    image[row_min:row_max+1, col_min:col_max+1],
                    background_mean)
        
        '''#Check fitdata
        print("Background: ", str(fitdata[0]))
        print("Amplitude: ", str(fitdata[1]))
        print("X: ", str(fitdata[2]))
        print("Y: ", str(fitdata[3]))
        print("Width_X: ", str(fitdata[4]))
        print("Width_Y: ", str(fitdata[5]))
        '''

        ##############
        #FIT CHECKING
        ##############
        if fitdata[0] <= 0 or fitdata[1] <=0:
            #print("Fit did not converge")
            #Fit did not converge
            continue
        
        if (np.abs(fitdata[5]/fitdata[4]) >= eccentricity_thresh or 
            np.abs(fitdata[4]/fitdata[5]) >= eccentricity_thresh):
            
            #print("Fit too eccentric")
            #Fit too eccentric
            continue
        
        if (fitdata[4] > (sigma_thresh * sigma) or 
            fitdata[4] < (sigma / sigma_thresh) or
            fitdata[5] > (sigma_thresh * sigma) or
            fitdata[5] < (sigma / sigma_thresh)):
            #print("Fit too unlike theoretical psf")
            #if fitdata[4] > (sigma_thresh * sigma) :
            #    print("spot x too large")
            #elif fitdata[4] < (sigma / sigma_thresh):
            #    print("spot x too small")
            #elif fitdata[5] > (sigma_thresh * sigma):
            #    print("spot y too large")
            #elif fitdata[5] < (sigma / sigma_thresh):   
            #    print("spot y too small")
            #Fit too unlike theoretical psf
            continue

        #Create a new Particle
        #TODO:        
        #p = cparticle.CParticle()
        p = pysm.new_cython.TempParticle()        
        
        #TODO: Implement Particle ID
        p.frame = frame
        p.position = np.array([row_min, row_max, col_min, col_max])
        
        p.height = fitdata[0]
        p.amplitude = fitdata[1]
        
        #TODO: FIX THIS BUG (switching of x and y)
        p.y = fitdata[2] + row_min + 1
        p.x = fitdata[3] + col_min + 1
        p.width_x = np.abs(fitdata[4])
        p.width_y = np.abs(fitdata[5])
        p.volume = (2 * np.pi * p.amplitude * p.width_x * p.width_y)
        
        # normalized volume for intensity moment descrimination in
        # linking step
        p.norm_volume = \
        	(2 * np.pi * (p.amplitude / (2**bit_depth - 1)) * 
			 p.width_x * p.width_y)
        
        # calculate signal to noise
        # (for our purposes a simple calc of amplitude of signal minus 
        # the background over the intensity of the background)
        p.sn = (p.amplitude + p.height) / p.height
        
        particle_list.append(p)


    print("Number of Particles found: " + str(len(particle_list)))
    '''
    mean = 0

    for p in particle_list:
        mean += p.height + p.amplitude
    mean /= len(particle_list)

    stdev = 0

    for p in particle_list:
        stdev += (mean - (p.height + p.amplitude))**2
    stdev = np.sqrt(stdev)
    stdev /= len(particle_list) + 1

    for p in particle_list[:]:
        if (p.height+p.amplitude) < (mean-stdev):
            particle_list.remove(p)

    print("mean: " + str(mean))
    print("stdev: " + str(stdev))
    print("Number of Particles remaining: " + str(len(particle_list)))
    '''

            

    return [particle_list,cutoff]


