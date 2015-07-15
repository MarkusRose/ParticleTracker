from Fileio import *
import random

a = []

for i in xrange(17):
    a.append(random.random())

setSysProps(a)

b = getSysProps()

print a
print b

c = []
for i in xrange(100):
    d = []
    for j in xrange(1000):
        e = []
        for k in xrange(10):
            e.append(random.random())
        d.append(e)
    c.append(d)

setDetection(c)
setTrackFile(c)

arr = getDetection()
print arr[0][0]

arrby = getTrackFile()
print arrby[0][0]
