import tracking
import Simulation.enzymeDiffuser as eD
import threading
import os

path = "D:/Benchmarking"

def handler(D,N,SR,rep):
    def calc():
        benchMarker(D,N,SR,rep)
    t = threading.Thread(target=calc)
    t.start()
    print("starting thread for {:}, {:}, {:}, {:}".format(D,N,SR,rep))
    return



def benchMarker(D,N,SR,rep):
    #D,N,F,path
    if not os.path.isdir(path+"/{:}-{:}-{:}-{:}".format(D,N,SR,rep)):
        os.mkdir(path+"/{:}-{:}-{:}-{:}".format(D,N,SR,rep))
    
    frames,tracks = eD.simwrapper(D,N,1000,path+'/{:}-{:}-{:}-{:}'.format(D,N,SR,rep))

    trtracks = tracking.doTrack_direct(frames, searchRadius=SR, minTracklen=1,linkRange=2, outfile='foundTracks.txt',path=path+'/{:}-{:}-{:}-{:}'.format(D,N,SR,rep))


    partlist = []
    trid = tracks[0].id
    for track in tracks:
        for frame in track.track:
            partlist.append([frame['frame'],frame['x'],frame['y'],track.id])

    def find_particle(c,p):
        id = 0
        for i in xrange(len(p)):
            if c[0] == p[i][0] and c[1] == p[i][1] and c[2] == p[i][2]:
                id = p[i][3]
                del p[i]
                break
            else:
                continue
        return id


    falselinks = 0
    for tr in trtracks:
        myid = 0
        for frame in tr.track:
            compare = [ frame['frame'], frame['x'], frame['y'], frame['particle_id']]
            saveid = find_particle(compare,partlist)

            if compare[0] == 0:
                continue
            
            if myid == 0:
                myid = saveid
            elif myid != saveid:
                falselinks += 1
                print 'Link found'
                break

    print falselinks

    fout = open(path+'/{:}-{:}-{:}-{:}/benchlog.txt'.format(D,N,SR,rep),'w')
    fout.write("falselinks = {:}".format(falselinks))
    fout.close()

    return falselinks

if __name__=="__main__":
    D = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90]
    N = [10,20,30,40,50,60,70,80,90,100]
    SR = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    repeats=10
    for d in D:
        for n in N:
            for sr in SR:
                for i in xrange(repeats):
                    handler(d,n,sr,i+1)

