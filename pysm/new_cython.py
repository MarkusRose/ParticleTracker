'''
Created on Feb 26, 2010

@author: jake
'''
#import cparticle
from scipy import ndimage, optimize
import numpy as np

#TESTING PURPOSES
#for particle in table:
#.......:     if particle['frame'] == cur_frame:
#.......:         new_particle = new_cython.TempParticle(particle.fetch_all_fields())
#.......:         frame.append(new_particle)
#.......:     else:
#.......:         result.append(frame)
#.......:         cur_frame = particle['frame']
#.......:         frame = []
#.......:         new_particle = new_cython.TempParticle(particle.fetch_all_fields())
#.......:         frame.append(new_particle)
class TempParticle(object):
    particle_id = 0
    frame = 0
    position=np.array([])
    time = 0
    
    sn = 0
    x = 0 
    y = 0
    width_x = 0
    width_y = 0
    height = 0
    amplitude = 0
    volume = 0
    norm_volume = 0
    next = np.array([])
    special = 0
    
    def __init__(self, particle=None):
        if particle:
            for var in particle.dtype.names:
                setattr(self, var, particle[var])
        return
        


#########################################################
# Particle Detection
#########################################################
def detect_particles_deflation(img,
                            bit_depth=16,
                            sigma=1.0,
                            frame=0,
                            local_max_window=3,
                            template_size=None,
                            signal_power=8,
                            eccentricity_thresh=1.5,
                            sigma_thresh=2,
                            deflations=2):
    
    img = img.astype(np.float)
    
    particles = []
    for i in xrange(deflations):
        img_filtered = gaussian_filter_image(img, sigma)
#        TODO: Changed testing out median filter implementation
#        (background_mean, 
#         background_std) = estimate_background(img_filtered)
        
        (background_mean, 
         background_std) = estimate_background_median(img, (21, 21))
        
        img_max_filter = local_maximum(img_filtered, local_max_window)
        img_max_filter = (img_max_filter >= background_mean + 
                          signal_power * background_std)
        
        gaussian_fit = fit_gaussians_2d(
                                    img, 
                                    sigma, 
                                    img_max_filter, 
                                    background_mean, 
                                    background_std,
                                    frame=frame,
                                    template_size=template_size,
                                    bit_depth=bit_depth,
                                    eccentricity_thresh=eccentricity_thresh,
                                    sigma_thresh=sigma_thresh)
        
        particles.extend(gaussian_fit)
        
        if i+1 < deflations:
            # Deflate Image
            for p in gaussian_fit:
                row_min = p.position[0]
                row_max = p.position[1]
                col_min = p.position[2]
                col_max = p.position[3]
                
                x = p.x - col_min
                y = p.y - row_min
                
                gauss = \
                    gaussian2d(p.height, p.amplitude, x, 
                               y, p.width_x, p.width_y)
                
                shape = ((row_max - row_min), (col_max - col_min))
                
                fitted_particle = np.fromfunction(gauss, shape) - p.height
                
                img[row_min:row_max, col_min:col_max] -= fitted_particle 
    
    return particles
    
def estimate_background_median(img, filter_size):
    median_img = ndimage.median_filter(img, filter_size)
    
    return (median_img.mean(), median_img.std())

def local_max_particles(
                     img, 
                     bit_depth, 
                     sigma, 
                     local_max_window=3,
                     template_size=None,
                     signal_power=8,
                     frame=0,
                     eccentricity_thresh=1.5,
                     sigma_thresh=2):
    
    img_filtered = gaussian_filter_image(img, sigma)
    
    img_max_filter = local_maximum(img_filtered, local_max_window)
    
    background_mean, background_std =\
        estimate_background_median(img, (21,21))

    gaussian_fit = fit_gaussians_2d(
                                    img, 
                                    sigma, 
                                    img_max_filter, 
                                    background_mean, 
                                    background_std,
                                    frame=frame,
                                    bit_depth=bit_depth,
                                    eccentricity_thresh=eccentricity_thresh,
                                    sigma_thresh=sigma_thresh)
    return gaussian_fit

def detect_particles(img, 
					 bit_depth, 
					 sigma, 
                     local_max_window=3,
                     template_size=None,
                     signal_power=8,
                     frame=0,
                     eccentricity_thresh=1.5,
                     sigma_thresh=2):
    
    img_filtered = gaussian_filter_image(img, sigma)
    
    (background_mean, 
     background_std) = estimate_background(img_filtered)
    
    img_max_filter = local_maximum(img_filtered, local_max_window)
    
    img_max_filter = (img_max_filter >= background_mean + 
                      signal_power * background_std)
    
    gaussian_fit = fit_gaussians_2d(
                                    img, 
                                    sigma, 
                                    img_max_filter, 
                                    background_mean, 
                                    background_std,
                                    frame=frame,
                                    bit_depth=bit_depth,
									eccentricity_thresh=eccentricity_thresh,
                     				sigma_thresh=sigma_thresh)
    
    return gaussian_fit
#########################################################
   
def gaussian_filter_image(img, sigma, order=1, 
                          boundry_condition = 'reflect'):
    """Gaussian Mid-pass Filter with HWHM sigma"""
    
    return ndimage.filters.gaussian_filter(img, sigma)

def estimate_background(img_normalized):
    """Estimates background mean and STD.  
    Rejects pixel values that are greater
    than 2 STD above the mean of the image.
    
    Input:
    img_normalized: normalized_image
    
    Output:
    tuple: (background_mean, backgound_std) 
    """
    
    #Compute the mean and STD of original normalized image
    mean = ndimage.measurements.mean(img_normalized)
    standard_dev = ndimage.measurements.standard_deviation(img_normalized)

    #recompute mean and standard deviation, apply treshold to image rejecting pixels
    #that are 2 STD above the orginal image mean. (reject signal pixels in background
    #calculation. (assumes background is normally distributed)
    
    #TODO: Changed
    #upper_bound = mean + (2 * standard_dev)
    upper_bound = mean + ( 1 * standard_dev)
    
    #mark values in image greater than upperbound
    #threshold_mask = stsci.threshhold(img_normalized, high=upper_bound).astype(numpy.int8)
    threshold_mask = (img_normalized <= upper_bound)
    
    #recalculate mean/std with all pixel values less than 2 std above the mean
    background_values = np.extract(threshold_mask, img_normalized)
    
    background_mean = np.mean(background_values)
    background_std = np.std(background_values)
    
    return (background_mean, background_std)

def local_maximum(img_convolved, window_size=3, 
                  boundry_condition='reflect'):
    """Computes local maximum based on scipy.ndimage maximum filter
    
    Input: gaussian convolved image
    
    Output: 
    filtered image showing detected local max pixels, all other pixels set to zero
    """
    
    max_filter = ndimage.maximum_filter(img_convolved, 
                                        size = window_size, 
                                        mode=boundry_condition)
    img_max_filter = img_convolved.copy()
    #set all pixels in convolved image not a local max to zero
    img_max_filter[(img_convolved != max_filter)] = 0    
    
    return img_max_filter

def gaussian2d(height, amplitude, center_x, 
               center_y, width_x, width_y):
    """Return 2d gaussian lamda(x,y) function"""
    
    height = float(height)
    amplitude = float(amplitude)
    width_x = float(width_x)
    width_y = float(width_y)
    
    return (lambda x,y: height + 
            amplitude*np.exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2))

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

def fit_gaussians_2d(img, 
					sigma, 
					img_max_filter, 
                    background_mean, 
                    background_std,
                    frame=0, 
                    template_size=None,
                    bit_depth=16,
                    eccentricity_thresh=1.5,
                    sigma_thresh=2):
    
    particle_list = []
    
    if template_size is None:
        template_size = 8 * np.ceil(sigma) - 1
    
    psf_range = np.floor(template_size/2)
    
    num_rows = img.shape[0]
    num_cols = img.shape[1]
    
    local_max_pixels = np.nonzero(img_max_filter)
    num_max_pixels = len(local_max_pixels[0])
    
    indices_row = local_max_pixels[0]
    indices_column = local_max_pixels[1]
    
    for i in xrange(num_max_pixels):
        
        row0 = int(indices_row[i])
        col0 = int(indices_column[i])
        
        row_min = row0 - psf_range
        row_max = row0 + psf_range #+1?? TODO:
        
        col_min = col0 - psf_range
        col_max = col0 + psf_range 
        
        if (row_min < 0 or row_max >= num_rows or
            col_min < 0 or col_max >= num_cols):
            #Peak too close to the edge to perform gauss fitting
            continue
        
        row_min = int(np.max(row_min, 0))
        col_min = int(np.max(col_min, 0))
        row_max = int(np.min(row_max, num_rows))
        col_max = int(np.max(col_max, num_rows))
    
        fitdata = fitgaussian2d(
                    img[row_min:row_max, col_min:col_max],
                    background_mean)
        
        ##############
        #FIT CHECKING
        ##############
        if fitdata[0] <= 0 or fitdata[1] <=0:
            #Fit did not converge
            continue
        
        if (np.abs(fitdata[5]/fitdata[4]) >= eccentricity_thresh or 
            np.abs(fitdata[4]/fitdata[5]) >= eccentricity_thresh):
            #Fit too eccentric
            continue
        
        if (fitdata[4] > (sigma_thresh * sigma) or 
			fitdata[4] < (sigma / sigma_thresh) or
            fitdata[5] > (sigma_thresh * sigma) or
            fitdata[5] < (sigma / sigma_thresh)):
            #Fit too unlike theoretical psf
            continue
        
        #Create a new Particle
        #TODO:        
        #p = cparticle.CParticle()
        p = TempParticle()        
        
        #TODO: Implement Particle ID
        p.frame = frame
        p.position = np.array([row_min, row_max, col_min, col_max])
        
        p.height = fitdata[0]
        p.amplitude = fitdata[1]
        
        #TODO: FIX THIS BUG (switching of x and y)
        p.y = fitdata[2] + row_min
        p.x = fitdata[3] + col_min
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
        
    return particle_list
        
