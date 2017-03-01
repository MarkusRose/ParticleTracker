

infile = "L:/Cel5A-6-22-10/45C/OD06/Experiment1/C-1-AnalyzedData/foundParticles.txt"

opfi = open(infile,'r')
line = opfi.readline()
frame = line.split()[1]

print frame

