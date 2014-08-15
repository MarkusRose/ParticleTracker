import detectParticles
import ctrack
import sys

img = [
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image1.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image2.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image3.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image4.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image5.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image6.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image7.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image8.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image9.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image10.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image11.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image12.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image13.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image14.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image15.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image16.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image17.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image18.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image19.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Particle diffusion/mol_image20.tif"]
'''
    "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image1.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image2.tif"]
    "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image3.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image4.tif",
    "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image5.tif"]
'''
sigma = 1
local_max_window = 3
signal_power = 14
bit_depth = 16
eccentricity_thresh = 1.5
sigma_thresh = 2
max_displacement = 50




def dataCorrect(particle_data):
    frame_count = 0
    output = True
    for frame in particle_data:
        frame_count += 1
        for particle in frame:
            if particle.frame != frame_count:
                output = False
                print ("nope, particle aint in right frame.")
                break
        if not output:
            break
    return output 
        

def testTracks(tracks):        
    print("Done creating tracks")
    print('ChooChoo! Track 29: \n' + str(tracks[29].track))
    print("Boy, you can give me a schein")
    for name in tracks[29].track.dtype.names:
        print(name + ": " + str(tracks[29].track[name]))
    return   

if __name__=="__main__":

    print('\n==== Start Localization and Detection ====')
    particle_data = detectParticles.multiImageDetect(img,sigma,local_max_window,signal_power,bit_depth,eccentricity_thresh,sigma_thresh)

#    if not dataCorrect(particle_data):
#        sys.exit("Particle data not correct")

    print('\n==== Start Tracking ====\n')
    tracks = ctrack.link_particles(particle_data,max_displacement)

    #testTracks(tracks)
    print("Done! FEIERABEND!")
