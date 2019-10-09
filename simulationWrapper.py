import Simulation.enzymeDiffuser as enzD
import Simulation.simSetup as simSetup

simulationPath = 'C:/Users/Markus/Desktop/TestSimWrapper'

simulationVariables = simSetup.createSystemProperties(path=simulationPath)
enzD.simulateTracks(inVars=simulationVariables,path=simulationPath,imageoutput=True)

