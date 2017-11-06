'''
Created on 2017-11-02 at 14:38EST

@author: Markus Rose
'''

import numpy as np
from skimage import io
#import skimage.external.tifffile as tf
import matplotlib.pyplot as plt
import matplotlib.patches as ptch
import matplotlib.path as pth
import random
import sys

from .videofig import videofig

#io.call_plugin('imread','tifffile')

def showDetections(images,detections):

    im = io.imread(images)

    if im.shape[0] != len(detections):
        print("Difference in detection frames and num of images.")
        print("Images: {:}".format(im.shape))
        print("Frames: {:}".format(len(detections)))
        #sys.exit(1)

    particles = []
    for j in range(im.shape[0]):
        frame = []
        for i in range(len(detections[j])):
            x = detections[j][i].x
            y = detections[j][i].y
            if not (np.isnan(x) or np.isnan(y)):
                frame.append(plt.Circle((x,y),radius=5,fill=False,edgecolor='r'))
        particles.append(list(frame))

    #redraw_fn draw frame f in a image sequence
    def redraw_fn(f, axes):
        img = im[f]
        if not redraw_fn.initialized:
            redraw_fn.prev = f
            redraw_fn.bb = particles
            image = axes.imshow(img, animated=True)
            for i in range(len(redraw_fn.bb[0])):
                axes.add_patch(redraw_fn.bb[0][i])
            redraw_fn.im = image
            redraw_fn.initialized = True
        else:
            redraw_fn.im.set_array(img)
            for i in range(len(redraw_fn.bb[redraw_fn.prev])):
                redraw_fn.bb[redraw_fn.prev][i].remove()
            for i in range(len(redraw_fn.bb[f])):
                axes.add_patch(redraw_fn.bb[f][i])
            redraw_fn.prev = f
        return

    redraw_fn.initialized = False

    videofig.videofig(len(im), redraw_fn, play_fps=2)
    return

def showTracks(images,tracks):

    im = io.imread(images)
    print((im.shape))


    particles = []
    steps = []
    id_frames = []
    colors = []
    trackids = []
    colstring = 'rgbymcwk'
    for i in range(len(tracks[1])):
        colors.append(colstring[i%len(colstring)])
        steps.append(np.transpose([tracks[0][i].track['x'],tracks[0][i].track['y']]))
    print(tracks[1])
    print(colors)

    
    paths = []
    for j in range(im.shape[0]):
        frame = []
        idf = []
        pathforframe = []
        for i in range(len(tracks[0])):
            x = tracks[0][i].track['x'][j]
            y = tracks[0][i].track['y'][j]
            if not (np.isnan(x) or np.isnan(y)):
                frame.append(plt.Circle((x,y),radius=5,fill=False,edgecolor=colors[i]))
                idf.append(tracks[1][i])
                pathforframe.append(ptch.PathPatch(pth.Path(steps[i][:j+1]),fill=False,edgecolor=colors[i]))
        paths.append(pathforframe)
        particles.append(list(frame))
        id_frames.append(list(idf))

    #redraw_fn draw frame f in a image sequence
    def redraw_fn(f, axes):
        img = im[f]
        if not redraw_fn.initialized:
            redraw_fn.prev = f
            redraw_fn.bb = particles
            redraw_fn.bb2 = paths
            image = axes.imshow(img, animated=True)
            for i in range(len(id_frames[0])):
                axes.add_patch(redraw_fn.bb[0][i])
                axes.add_patch(redraw_fn.bb2[0][i])
            redraw_fn.im = image
            redraw_fn.initialized = True
        else:
            redraw_fn.im.set_array(img)
            for i in range(len(id_frames[redraw_fn.prev])):
                redraw_fn.bb[redraw_fn.prev][i].remove()
                redraw_fn.bb2[redraw_fn.prev][i].remove()
            for i in range(len(id_frames[f])):
                axes.add_patch(redraw_fn.bb[f][i])
                axes.add_patch(redraw_fn.bb2[f][i])
            redraw_fn.prev = f
        return

    redraw_fn.initialized = False

    videofig.videofig(len(im), redraw_fn, play_fps=2)
    return

