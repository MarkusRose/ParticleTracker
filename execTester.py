import detectParticles


img = "/home/markus/LittleHelpers/MatlabSimulations/Static Particles Multiple Frames/mol_image9.tif"
sigma = 1
local_max_window = 3
signal_power = 14
bit_depth = 16
frame = 0
eccentricity_thresh = 1.5
sigma_thresh = 2


        
if __name__=="__main__":
    particles = []

    particles = detectParticles.detectParticles(
            img,
            sigma,
            local_max_window,
            signal_power,
            bit_depth,
            frame,
            eccentricity_thresh,
            sigma_thresh)

    #print particles

    outfile = open("foundParticles.txt",'w')
    outfile.write("x      y \n")
    for p in particles:
        outfile.write('{:.2f}'.format(p.x) + ' ' + '{:.2f}'.format(p.y) + ' ' + str(p.height+p.amplitude) + ' ' + str(p.sn) + '\n')
