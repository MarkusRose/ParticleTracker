import tracking as tr
import Simulation.enzymeDiffuser as eD

path = "D:\Benchmarking"
frames,tracks = eD.simwrapper(10,20,10,path)

trtracks = tr.doTrack_direct(frames, searchRadius=10, minTracklen=1,linkRange=2, outfile=path+'/foundTracks.txt',path=path)

count = 0
for tr in trtracks:
    print tr.track['frame']
    for f in tr.track['frame']: 
        print tr.track[tr.track['frame']==f]['frame']
        print tracks[count].track[tracks[count].track['frame']==f]['frame']
    count += 1
    if count >= len(tracks):
        break
