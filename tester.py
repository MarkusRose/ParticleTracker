import Detection.convertFiles as cF

def main():
    pd = cF.readDetectedParticles("foundParticles.txt")
    print len(pd)

if __name__=="__main__":
    main()
