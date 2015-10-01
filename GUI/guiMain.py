import Tkinter
import sys

import guiAnalysis
import guiTracking
import guiDetection
import guiSimulation

class mainWindow(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        #self.geometry("320x400")

        def runSimulation():
            #window = Tkinter.Toplevel(None)
            app = guiSimulation.Simulation_App(self)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            
        def runDetection():
            app = guiDetection.guiDetection(self)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)

        def runTracking():
            app = guiTracking.guiTracking(self)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
        
        def runDetandTrack():
            app = guiDetection.guiDetandTrack(self)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
        
        def runAnalysis():
            print "Analyzing"
        
        simbutton = Tkinter.Button(self, text=u"Simulation",command=runSimulation)
        simbutton.grid(column=0,row=1,sticky="EW")
        detbutton = Tkinter.Button(self, text=u"Detection",command=runDetection)
        detbutton.grid(column=0,row=2,sticky="EW")
        trabutton = Tkinter.Button(self, text=u"Tracking",command=runTracking)
        trabutton.grid(column=0,row=3,sticky="EW")
        detatrabutton = Tkinter.Button(self, text=u"Detect and Track",command=runDetandTrack)
        detatrabutton.grid(column=0,row=3,sticky="EW")
        anabutton = Tkinter.Button(self, text=u"Analysis",command=runAnalysis)
        anabutton.grid(column=0,row=4,sticky="EW")
        exibutton = Tkinter.Button(self, text=u"Quit", command=self.destroy)
        exibutton.grid(column=0,row=5,sticky="EW")
        #exibutton.pack()
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)


if __name__=="__main__":
    app = mainWindow(None)
    app.title("MainWindow")
    app.mainloop()
