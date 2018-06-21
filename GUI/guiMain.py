try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import sys

from GUI import guiAnalysis
from GUI import guiTracking
from GUI import guiDetection
from GUI import guiDetandTrack
from GUI import guiSimulation
from GUI import guiVisualization

class mainWindow(tk.Tk):
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        #self.geometry("320x400")

        def runSimulation():
            self.simwin = tk.Toplevel(self)
            self.simwin.title("Simulation")
            app = guiSimulation.Simulation_App(self.simwin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.simwin.winfo_width()
            h = self.simwin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.simwin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return
            
        def runDetection():
            self.detwin = tk.Toplevel(self)
            self.detwin.title("Detection")
            app = guiDetection.guiDetection(self.detwin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.detwin.winfo_width()
            h = self.detwin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.detwin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return

        def runTracking():
            self.trackwin = tk.Toplevel(self)
            self.trackwin.title("Tracking")
            app = guiTracking.guiTracking(self.trackwin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.trackwin.winfo_width()
            h = self.trackwin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.trackwin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return
        
        def runDetandTrack():
            self.dettrackwin = tk.Toplevel(self)
            self.dettrackwin.title("Detection and Tracking")
            app = guiDetandTrack.guiDetandTrack(self.dettrackwin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.dettrackwin.winfo_width()
            h = self.dettrackwin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.dettrackwin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return
        
        def runAnalysis():
            self.anawin = tk.Toplevel(self)
            self.anawin.title("Analysis of Tracks")
            app = guiAnalysis.guiAnalysis(self.anawin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.anawin.winfo_width()
            h = self.anawin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.anawin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return
        
        def runVis():
            self.Viswin = tk.Toplevel(self)
            self.Viswin.title("Visualization")
            app = guiVisualization.guiVisualization(self.Viswin)
            app.grid(column=1,row=0,rowspan=12,sticky="NWSE")
            app.grid_columnconfigure(0,weight=1)
            self.update()
            w = self.Viswin.winfo_width()
            h = self.Viswin.winfo_height()
            posx = self.winfo_x()+self.winfo_width()
            posy = self.winfo_y()
            self.Viswin.geometry("{:}x{:}+{:}+{:}".format(w,h,posx,posy))
            return
        
        simbutton = tk.Button(self, text="Simulation",command=runSimulation)
        simbutton.grid(column=0,row=1,sticky="EW")
        detbutton = tk.Button(self, text="Detection",command=runDetection)
        detbutton.grid(column=0,row=2,sticky="EW")
        trabutton = tk.Button(self, text="Tracking",command=runTracking)
        trabutton.grid(column=0,row=3,sticky="EW")
        detatrabutton = tk.Button(self, text="Detect and Track",command=runDetandTrack)
        detatrabutton.grid(column=0,row=4,sticky="EW")
        anabutton = tk.Button(self, text="Analysis",command=runAnalysis)
        Visbutton.grid(column=0,row=5,sticky="EW")
        exibutton = tk.Button(self, text="Quit", command=self.destroy)
        anabutton.grid(column=0,row=6,sticky="EW")
        Visbutton = tk.Button(self, text="Visualize",command=runVis)
        exibutton.grid(column=0,row=7,sticky="EW")
        #exibutton.pack()
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(False,False)
        self.update()
        self.minsize(self.winfo_width()+100,self.winfo_height())

        return


if __name__=="__main__":
    app = mainWindow(None)
    app.title("MainWindow")
    app.mainloop()
