import numpy as np

f = open("toanalyze.txt",'r')

x = np.zeros((6,2))
y = np.zeros((6,2))

#f.readline()

i = 0
for line in f:
    print i
    values = line.split()
    x[i] = values[0:2]
    y[i] = values[2:4]
    i += 1

def diffPos(x,y):
    diff = np.zeros((len(x)))
    for i in xrange(len(x)):
        diff[i] = np.sqrt((x[i,0]-y[i,0])**2 + (x[i,1]-y[i,1])**2)
    return diff

def meanAndStd(diff):
    sum = 0
    std = 0

    for d in diff:
        sum += d

    sum /= len(diff)

    for d in diff:
        std += (d - sum)**2

    std = np.sqrt(std/(len(diff)-1))

    return (sum,std)

if __name__=="__main__":
    achso = meanAndStd(diffPos(x,y))
    print("Mean difference: " + str(achso[0]))
    print("Std difference: " + str(achso[1]))
