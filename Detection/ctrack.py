'''
Created on Feb 26, 2010

@author: jake
'''
"""
Created on Feb 8, 2010

@author: jake
"""
#module imports
import os
import time
import sys
import pysm.new_cython
import System.Fileio as Fileio
from scipy import io
import string
import random

import numpy as np
#cimport numpy as np


class ParticleTrack(object):
    
    struct_type = [('particle_id', np.str_),
                   ('frame', np.uint32),
                   ('sn', np.double),
                   ('x', np.double),
                   ('y', np.double),
                   ('width_x', np.double),
                   ('width_y', np.double),
                   ('height', np.double),
                   ('amplitude', np.double),
                   ('volume', np.double)]
    
    def __init__(self, id, num_elements):
        self.track = np.empty(num_elements, 
                              dtype=self.struct_type)
        self.id = id
        
        for name in self.track.dtype.names:
            if name == 'particle_id':
                self.track[name].fill(self.id)
            elif name == 'frame':
                self.track[name].fill(0)
            else:
                self.track[name].fill(np.nan)
                
    def insert_particle(self, particle, frame):
        for name in self.track.dtype.names:
            #TODO: FIX ERROR
            try:
                self.track[name][frame] = getattr(particle, name)
            except:
                pass
        return    
    
def writeTrajectories(tracks,filename="foundTracks.txt"):
    outfile = open(filename,'w')
    track_num = 0
    for track in tracks:
        track_num += 1
        outfile.write('\n\n# -Track {:2.0f} -------------------------------------\n'.format(track_num))
        outfile.write("# frame    x      y    width_x   width_y  height  amplitude     sn     volume    Particle-ID\n")
        for particle in track.track:
            #print particle['x']
            if np.isnan(particle['x']):
                outfile.write("# ")
            for name in particle.dtype.names:
                if name == 'particle_id' or name == 'sn':
                    continue
                outfile.write("{:3.4f} ".format(particle[name]))
            outfile.write("{:3.4f} ".format(particle['sn']))
            outfile.write("{:}".format(track.id))
            outfile.write("\n")

    outfile.close()
    print("Done writing Tracks")
    print("Number of Tracks found: {:}".format(len(tracks)))
    return

def makeParticle(frame,x,y,width_x,width_y,height,amplitude,part_id):
        #Create a new Particle
        #TODO:        
        #p = cparticle.CParticle()
        p = pysm.new_cython.TempParticle()        
        
        #TODO: Implement Particle ID
        p.frame = frame
        
        p.height = height 
        p.amplitude = amplitude
        
        #TODO: FIX THIS BUG (switching of x and y)
        p.y = y
        p.x = x
        p.width_x = width_x
        p.width_y = width_y
        p.volume = (2 * np.pi * p.amplitude * p.width_x * p.width_y)
        
        # normalized volume for intensity moment descrimination in
        # linking step
        #p.norm_volume = (2 * np.pi * p.amplitude * p.width_x * p.width_y)
        
        #TODO: FIX THIS!!!
        # calculate signal to noise
        # (for our purposes a simple calc of amplitude of signal minus 
        # the background over the intensity of the background)
        if p.height != 0:
            p.sn = (p.amplitude + p.height) / p.height
        p.particle_id = part_id

        return p


def readTrajectoriesFromFile(filename,minTrackLen):
    infile = open(filename,'r')
    boo = True
    frame = -2
    num_frames = 0

    for line in infile:
        #print line
        if line.strip():
            if boo:
                boo = False
            frame += 1
        else:
            if not boo:
                num_frames = frame
                break
    infile.close()

    if num_frames == 0:
        num_frames = frame
    
    infile = open(filename,'r')
    tracks = []
    tracknum = 0
    liste = []
    boo = True
    frame = -2
    partpos = 0

    particle_track = ParticleTrack(id=1,num_elements=0)
    
    for line in infile:
        if line.strip():
            if boo:
                tracknum += 1
                particle_track = ParticleTrack(id=1, num_elements=num_frames)
                boo = False
            if not (frame < 0):
                if not line[0] == "#":
                    f,x,y,width_x,width_y,height,amplitude,z,z = line.split()
                    particle = makeParticle(round(float(f)),float(x),float(y),float(width_x),float(width_y),float(height),float(amplitude))
                    particle_track.insert_particle(particle, particle.frame)
                    partpos += 1
            frame += 1
        else:
            if not boo:
                tracks.append(particle_track)
                if partpos >= minTrackLen:
                    liste.append(tracknum)
                frame = -2
                partpos = 0
                boo = True
    if len(particle_track.track) != 0:
        tracks.append(particle_track)
        if partpos >= minTrackLen:
            liste.append(tracknum)

    infile.close()

    saveTN = open("SuggestedTrajectories.txt",'w')
    saveTN.write("Use the following tracks: \n" + str(liste))
    saveTN.close()

    return tracks,liste


def link_particles(particle_data, max_displacement,
                   link_range=2, 
                   min_track_len=10,
                   outfile="foundTracks.txt"):
    ''' Initialize Particle Tracking variables'''
    #Array Index Variables
    #cdef Py_ssize_t i, j, k, m, n 
    #cdef Py_ssize_t frame, particle
    #cdef Py_ssize_t num_frames, num_particles
    
    num_frames = len(particle_data)
    max_cost = max_displacement**2
    #print("Number of frames: " + str(num_frames))
    
    if len(particle_data) < 2:
        raise Exception("Number of frames must be larger than 2")
        return
    
    #if linkrange is too big set to correct number of values
    if num_frames < (link_range + 1):
        print("Change link_range")
        link_range= num_frames - 1

    for i in range(num_frames):
        num_particles = len(particle_data[i])
        for j in range(num_particles):
            particle = particle_data[i][j]
            particle.next = np.array([[-1] * link_range], dtype=np.int)
            particle.special = 0


    #print particle_data[0][16].next.shape
    ''' Begin Tracking process'''
    count = 0
    print('_'*52)
    sys.stdout.write("[")
    sys.stdout.flush()
    for frame in range(num_frames - link_range):
        #TODO: DEBUG
        #print ("Image %s Processing" % (frame+1))
        aaa = int(frame * 50/(num_frames - link_range))
        if aaa > count:
            sys.stdout.write("#"*(aaa-count))
            sys.stdout.flush()
            count += aaa-count
        
        cur_link_range = link_range
        num_particles = len(particle_data[frame])
        
        for link in range(cur_link_range):
            max_cost = ((link + 1) * max_displacement)**2
            num_particles_next = len(particle_data[frame + (link + 1)])
            #print num_particles_next
            
            #Set up cost matrix
            cost_matrix = np.zeros((num_particles + 1, num_particles_next + 1), 
                                dtype=np.float64)
            
            #Set up association matrix
            association_matrix = np.zeros((num_particles + 1, num_particles_next + 1),
                                dtype=np.intc)
            
            cur_particles = particle_data[frame]
            link_particles = particle_data[frame + (link + 1)]
            
            ####################
            # Build Cost Matrix
            ####################
            #print('building cost matrix')
            cost_matrix = build_cost_matrix(
                                cur_particles,
                                link_particles,
                                max_cost,
                                cost_matrix)
            
            ######################
            # Build Assoc. Matrix
            ######################
            #print('build association matrix')
            association_matrix = lap_assoc_matrix(
                                    max_cost,
                                    association_matrix,
                                    cost_matrix)
            
            ######################
            # Link Particles
            ######################
            #print('done with matrices')

            for i in range(num_particles):
                cur_particle = particle_data[frame][i]

                for j in range(num_particles_next):
                    #print((i,j))
                    #print(cur_particle.next)
                    if association_matrix[i, j] == 1:
                        #print((i,j))
                        #print(cur_particle.next.shape)
                        #print("frame: " + str(frame) + ", link: " + str(link) + ", current particle: " + str(i))
                        #print(len(cur_particle.next.shape))
                        #print(cur_particle.next.shape)
                        #if j >= len(cur_particle.next[0]):
                        #    print("Problem: j out of bounds ( j > len(cur_particle.next[0]))")
                        #TODO problem with link_range = 2 (out of bounds)
                        cur_particle.next[0][link] = j
                        
        #print("Done with linking Particles for image " + str(frame+1))

        '''
        m = 0
        print(m)
        if m == (num_frames - cur_link_range - 1) and cur_link_range > 1:
            cur_link_range -= 1
            '''
    
    sys.stdout.write("#"*(50-aaa)+"]\n")
    #######################################
    # At Last Frame all Trajectories End
    #######################################
    for i in range(len(particle_data[num_frames - 1])):
        particle = particle_data[num_frames - 1][i]
        particle.special = 0
        for j in range(link_range):
            particle.next[0][j] = -1
            
    
    #######################################
    # Build Trajectories
    ######################################
    trajectories = []
    
    for i in range(num_frames):
        
        num_particles = len(particle_data[i])
        for j in range(num_particles):
            
            particle = particle_data[i][j]
            
            if particle.special == 0:
                particle.special = 1
                found = -1
                
                for n in range(link_range):
                    # If not dummy particle stop looking
                    if particle.next[0][n] != -1:
                        found = n
                        break
                
                # If particle is not linked to any other go to the
                # next particle and don't add a trajectory
                if found == -1:
                    continue
                
                # If particle is linked to a "real" particle that
                # was already linked break trajectory and start again
                # from the next particle.  Don't generate a trajectory.
                link_index = particle.next[0][n]
                #print( i+n+1, link_index )
                #print( len(particle_data),len(particle_data[i+n+1]) )
                #TODO: List index out of range
                linked_particle = particle_data[i + n + 1][link_index]
                
                if linked_particle.special == 1:
                    continue
                
                # Else, particle is linked to another "real" particle
                # that is not already linked.  Build new trajectory
                track_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
                particle_track = ParticleTrack(id=track_id, 
                                               num_elements=num_frames)
                
                particle_track.insert_particle(particle, 
                                               particle.frame)
                
                
                k = i
                m = j
                
                ##############################################
                # Build Trajectory from current particle
                ##############################################
                
                while True:
                    found = -1
                    cur_particle = particle_data[k][m]
                    
                    for n in range(link_range):
                        
                        if cur_particle.next[0][n] != -1:
                            link_index = cur_particle.next[0][n]
                            try:
                                linked_particle = particle_data[k + n + 1][link_index]
                            except IndexError:
                                print "IndexError for this line"
                                print "linked_particle {:}, index {:}".format(len(particle_data),k+n+1)
                                print "linked_particle-sublength {:}, index {:}".format(len(particle_data[k+n+1]),link_index)
                                sys.exit(1)
                                
                            # If particle is linked to a real 
                            # particle that is not already linked, 
                            # continue building the trajectory
                            if linked_particle.special == 0:
                                found = n
                                break
                           
                            # If current particle is linked to a 
                            # real particle that is not already linked
                            # stop building the trajectory
                            else:
                                break
                    
                    # Stop building the trajectory
                    # when link is not found
                    if found == -1:
                        break
                    
                    m = cur_particle.next[0][found]
                    k += found + 1
                    
                    if m != -1 and particle_data[k][m] is not None:
                        # If linked particle is a "real" particle
                        # Build Trajectory
                        #print("attach nextparticle to track " + str(len(trajectories)))
                        #print("frame: " + str(k))
                        linked_particle = particle_data[k][m]
                        linked_particle.special = 1
                    
                        particle_track.insert_particle(linked_particle,
                                                   linked_particle.frame)
                        #print("Linked Particle frame: " + str(linked_particle.frame))
                        #print("Particle Track " + str(len(trajectories)) + ": " + str(particle_track.track['x']))
                    else:
                        print("Stopping track here: " + str(len(particle_track)))
                        #TODO:
                        # Check this logic, should m ever be negative? 
                        # If current
                        break
                
                #################################################
                
                trajectories.append(particle_track)   
    
    print("Done Linking")
    writeTrajectories(trajectories,filename=outfile)
    #Fileio.setTrackFile(trajectories)
    return trajectories
                        
def build_cost_matrix(
    particles_1,
    particles_2,
    max_cost,
    cost_matrix):
    
    #cdef Py_ssize_t num_particles, num_particles_next
    num_particles = cost_matrix.shape[0]-1
    num_particles_next = cost_matrix.shape[1]-1
    
    #cdef Py_ssize_t i, j
    for i in range(num_particles):
        for j in range(num_particles_next):
            cost_matrix[i,j] = \
                ((particles_1[i].x - particles_2[j].x)**2 + 
                 (particles_1[i].y - particles_2[j].y)**2)
        
    for i in range(num_particles + 1):
        cost_matrix[i, num_particles_next] = max_cost
    
    for j in range(num_particles_next + 1):
        cost_matrix[num_particles, j] = max_cost
        
    cost_matrix[num_particles, num_particles_next] = 0.0
    
    return cost_matrix
                                
def lap_assoc_matrix(
        max_cost,
        association_matrix, 
        cost_matrix):
    
    #cdef Py_ssize_t  num_particles, num_particles_next
    
    #association matrix is number of particles + dummy column
    num_particles = association_matrix.shape[0]-1 
    num_particles_next = association_matrix.shape[1]-1 
    
    #array index variables
    #cdef Py_ssize_t i, j, k, prev
    #cdef Py_ssize_t prev_i, prev_j
    #cdef Py_ssize_t prevS_x, prevS_y
    #cdef Py_ssize_t x, y
    #
    #cdef int ok
    #cdef double reduced_cost, min
    
    #loop over rows
    for i in range(num_particles):
        min = max_cost
        prev = 0
        
        #loop over cols
        for j in range(num_particles_next):
            ok = 1
            
            for k in range(num_particles + 1):
                if association_matrix[k, j] == 1:
                    ok = 0
                    break
            
            #cannot link to particle, try next column
            if ok == 0:
                continue
            
            #found link to next particle
            if cost_matrix[i, j] < min:
                min = cost_matrix[i,j]
                association_matrix[i, prev] = 0
                prev = j
                association_matrix[i, j] = 1
        
        #Check to see if current particle is linked to dummy column/row
        if min == max_cost:
            association_matrix[i, prev] = 0
            association_matrix[i, num_particles_next] = 1
    
    #look for columns that are zero (no links)
    #TODO: CHECK THIS
    for j in range(num_particles_next):
        ok = 1
        
        for i in range(num_particles + 1):
            if association_matrix[i,j] == 1:
                ok = 0

        if ok == 1:
            association_matrix[num_particles, j] = 1
    
    reduced_cost = 0.0
    min = -1.0
    
    while (min < 0.0):
        
        #reinitalize values through each iteration 
        #when optimizing the assoc. matrix
        min = 0.0
        prev_i = 0
        prev_j = 0
        prevS_x = 0
        prevS_y = 0
        
        for i in range(num_particles + 1):
            for j in range(num_particles_next + 1):
                
                if i == num_particles and j == num_particles_next:
                    continue
                
                #Calculate the reduced cost
                if (association_matrix[i, j] == 0 and 
                    cost_matrix[i, j] <= max_cost):
                    
                    #look along the x-axis including
                    #the dummy particles
                    for k in range(num_particles + 1):
                        if association_matrix[k, j] == 1:
                            x = k
                            break
                    
                    #look along the y-axis including
                    #the ummy particles
                    for k in range(num_particles_next + 1):
                        if association_matrix[i, k] == 1:
                            y = k
                            break
                    
                    #z is the reduced cost
                    if j == num_particles_next:
                        x = num_particles
                    
                    if i == num_particles:
                        y = num_particles_next
                    
                    reduced_cost = (cost_matrix[i, j] + cost_matrix[x, y] -
                                    cost_matrix[i, y] - cost_matrix[x, j])
                                    
                    #TODO: Debug XXX:
                    #if reduced_cost > -1.0e-10:
                    #   reduced_cost = 0.0
                    
                    if reduced_cost < min:
                        min = reduced_cost
                        prev_i = i
                        prev_j = j
                        prevS_x = x
                        prevS_y = y
        
        if min < 0.0:
            association_matrix[prev_i, prev_j] = 1
            association_matrix[prevS_x, prevS_y] = 1
            association_matrix[prev_i, prevS_y] = 0
            association_matrix[prevS_x, prev_j] = 0
    
    return association_matrix

#cdef class ParticleTrack:
#    """SM Particle Track Data Structure"""
#    cdef public np.uint32_t track_id
#    cdef public np.ndarray[np.uint32_t, ndim=1] id
#    cdef public np.ndarray[np.uint32_t, ndim=1] frame
#    cdef public np.ndarray[np.float64_t, ndim=1] sn
#    cdef public np.ndarray[np.float64_t, ndim=1] x
#    cdef public np.ndarray[np.float64_t, ndim=1] y
#    cdef public np.ndarray[np.float64_t, ndim=1] width_x
#    cdef public np.ndarray[np.float64_t, ndim=1] width_y
#    cdef public np.ndarray[np.float64_t, ndim=1] height
#    cdef public np.ndarray[np.float64_t, ndim=1] amplitude
#    cdef public np.ndarray[np.float64_t, ndim=1] volume

#class ParticleTrack(object):
#    def __init__(self, id, num_elements):
#        self.track_id = id
#        self.particle_id = \
#            np.empty(num_elements, dtype=np.uint32).fill(np.nan)
#        self.frame = \
#            np.empty(num_elements, dtype=np.unit32).fill(np.nan)
#        self.sn = \
#            np.empty(num_elements, dytpe=np.uint32).fill(np.nan)
#        self.x = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.y = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.width_x = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.width_y = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.height = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.amplitude = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
#        self.volume = \
#            np.empty(num_elements, dtype=np.float64).fill(np.nan)
