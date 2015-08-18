from Fileio import *
import random
import math

a = []

for i in xrange(19):
    a.append(random.random())

setSysProps(a)

b = getSysProps()

print a
print b

