#Makefile for Project "Search for Particle"

all: runProg
	
runProg: readImage.py execTester.py
	python main.py
