import numpy as np
import matplotlib.pyplot as plt
import sys


#read in Tracks
def readTracks(infile):
    fopen = open(infile,'r')

    tracks = []
    track = []
    brt = False

    for line in fopen:

        if len(line.strip()) == 0:
            if brt:
                brt = False
                tracks.append(np.array(track))
                del track
            continue
        elif line[0] == '#':
            if not brt:
                brt = True
                track = []
            continue
        track.append(np.array(list(map(float,line.split()[:-1]))))

    if len(track) > 0:
        tracks.append(np.array(track))
        del track

    return tracks


def combineTracks(tracks):
    lastpart = np.zeros((len(tracks[0][0])))
    combtr = [np.array(lastpart)]
    for tr in tracks:
        lastpart = np.array(combtr[-1])
        for part in range(1,len(tr),1):
            outpart = []
            for i in range(len(tr[0])):
                if i < 3:
                    outpart.append(tr[part][i] - tr[0][i]+lastpart[i])
                else:
                    outpart.append(tr[part][i])
            combtr.append(np.array(outpart))
    return np.array(combtr)



def sci(track,L):
    v = np.zeros((len(track)-1,3),dtype=np.float_)
    N = int(track[-1][0] - track[0][0])
    print(N)
    sys.stdout.flush()
    for i in range(1,len(track),1):
        dt = track[i][0] - track[i-1][0]
        dx = track[i][1] - track[i-1][1]
        dy = track[i][2] - track[i-1][2]
        v[i-1][0] = track[i-1][0]
        v[i-1][1] = dx*1.0/dt
        v[i-1][2] = dy*1.0/dt
    #print v    
    
    CofK = []
    print("Starting")
    sys.stdout.flush()
    for k in range(L):
        Uk = np.zeros((int((N-k)/L),2),dtype=np.float_)
        for j in range(len(Uk)):
            istart = j*L+k
            iend = istart + L
            iter = 0
            vsum = np.array([0,0],dtype=np.float_)
            counter = 0
            while iter < len(v) and v[iter][0] < iend:
                if v[iter][0] < istart:
                    iter+=1
                elif v[iter][0] == istart:
                    vsum[0] += v[iter][1]
                    vsum[1] += v[iter][2]
                    counter += 1
                    istart += 1
                    iter+=1
                elif v[iter][0] > istart:
                    istart += 1
            if counter != 0:
                Uk[j] = vsum/counter
        print(Uk)
        C_k = []
        for i in range(L-1,N-2*L+1,1):
            j = int((i-k)/L)
            C_k.append((Uk[j]*Uk[j+1]).sum()/(np.linalg.norm(Uk[j])*np.linalg.norm(Uk[j+1])))
        CofK.append(np.array(C_k,dtype=np.float_))
        print(k)
        sys.stdout.flush()
    
    #CofK = np.array(CofK)
    print(CofK)
    sys.stdout.flush()
    return np.average(CofK,axis=0)


def doSCI(trackfile):
    tracks = readTracks(trackfile)
    ct = combineTracks(tracks[:])
    C = sci(ct,1)
    print(C)
    return

if __name__=="__main__":
    doSCI()
    
