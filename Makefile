#Makefile for Project "Search for Particle"

all: runProg


runProg: readImage.py main.py
	python main.py
