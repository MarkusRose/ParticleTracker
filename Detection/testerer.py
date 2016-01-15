import numpy as np
import random

toDo = []

a = np.zeros((10,10))

counter = 0
while counter < 20:
    x = random.randint(0,9)
    y = random.randint(0,9)
    if a[x,y] == -1:
        continue
    a[x,y] = -1
    counter += 1

print a
print counter


def checkNN(i,j,clco):
    if i > 0 and a[i-1,j] == -1:
        a[i-1,j] = clco
        toDo.append([i-1,j])
    if i < len(a)-1 and a[i+1][j] == -1:
        a[i+1,j] = clco
        toDo.append([i+1,j])
    if j > 0 and a[i,j-1] == -1:
        a[i,j-1] = clco
        toDo.append([i,j-1])
    if j < len(a[0])-1 and a[i,j+1]:
        a[i,j+1] = clco
        toDo.append([i,j+1])


clco = 0
for i in xrange(len(a)):
    for j in xrange(len(a[i])):
        if a[i,j] == 0:
            continue
        elif a[i,j] == -1:
            clco += 1
            a[i,j] = clco
            toDo.append([i,j])
            while len(toDo) > 0:
                checkNN(toDo[0][0],toDo[0][1],clco)
                del toDo[0]
print clco

print a


