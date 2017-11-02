'''
Created on 2017-11-02 at 14:38EST

@author: Markus Rose
'''

import numpy as np
from skimage import io
#import skimage.external.tifffile as tf
import matplotlib.pyplot as plt
import pylab as pl

from videofig import videofig

#io.call_plugin('imread','tifffile')

path = 'SimulatedImages/'
anapath= 'Analysis/'

im = io.imread(path+'SimulatedImages.tif')
print(im.shape)



#redraw_fn draw frame f in a image sequence
def redraw_fn(f, axes):
    img = im[f]
    if not redraw_fn.initialized:
        image = axes.imshow(img, animated=True)
        bb = plt.Circle((30,30),radius=5,fill=False,edgecolor="red")
        axes.add_patch(bb)
        redraw_fn.im = image
        redraw_fn.bb = bb
        redraw_fn.initialized = True
    else:
        redraw_fn.im.set_array(img)
        redraw_fn.bb.center = (np.random.randint(0,high=50,size=2))

redraw_fn.initialized = False

videofig.videofig(len(im), redraw_fn, play_fps=3)


