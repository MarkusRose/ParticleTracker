from . import tracking
from . import Simulation.enzymeDiffuser as eD
import threading
try:
    import queue
except ImportError:
    import queue as Queue
import time
import os

path = "D:/Benchmarking"

exitFlag = 0
workQueue = queue.Queue(8)
dataQueue = queue.Queue(20)
queueLock = threading.Lock()
dataLock = threading.Lock()
results = []

class myThread(threading.Thread):
    def __init__(self,threadID,name,q,dq):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.dq = dq
        return

    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q,self.dq)
        print("Exiting " + self.name)

def process_data(threadName, q, dq):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.emtpy():
            data = q.get()
            queueLock.release()
            print("%s processing %s" % (threadName,data))
            result = benchMarker(data)
            dataLock.acquire()
            dq.put(result)
            dataLock.release()
        else:
            queueLock.release()
        time.sleep(1)

def benchMarker(data):
    D,N,SR,rep = data
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
        for i in range(len(p)):
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
                print('Link found')
                break

    print(falselinks)

    fout = open(path+'/{:}-{:}-{:}-{:}/benchlog.txt'.format(D,N,SR,rep),'w')
    fout.write("falselinks = {:}\n".format(falselinks))
    fout.close()

    return D, N, SR, rep, 1000, falselinks

if __name__=="__main__":
    D = [0.1,0.5,1,5,10,50,90]
    N = [10,20,40,80]
    SR = [2,3,4,5,6,7,8,9,10,15,20,30]
    repeats=5

    dataForThreads = []
    for d in D:
        for n in N:
            for sr in SR:
                for i in range(repeats):
                    dataForThreads.append([d,n,sr,i+1])

    threads = []
    for i in range(8):
        thread = myThread(i+1,"Thread-{:}".format(i+1),workQueue,dataQueue)
        thread.start()
        threads.append(thread)

    for data in dataForThreads:
        while workQueue.full():
            continue
        queueLock.acquire()
        workQueue.put(data)
        queueLock.release()
        if dataQueue.full():
            dataLock.acquire()
            while not dataQueue.emtpy():
                results.append(dataQueue.get())
            dataLock.release()

    while not dataQueue.empty():
        dataLock.acquire()



    fout = open(path+'summarybench.txt','w')
    fout.write("#Dif,  numParts,   S/N,   Frames, Reps,  Falselinks\n ")
    for d in D:
        for n in N:
            for sr in SR:
                for i in range(repeats):
                    print()
                    print(("starting {:}, {:}, {:}, {:}".format(d,n,sr,i)))
                    dif,num,sign,reps,frames,falselinks = benchMarker(d,n,sr,i+1)
                    fout.write("{:} {:} {:} {:} {:} {:}\n".format(dif,num,sign,frames,reps,falselinks))
    fout.close()
