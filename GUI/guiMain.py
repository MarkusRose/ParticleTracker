import Tkinter
import sys

import guiAnalysis
import guiTracking
import guiDetection
import guiDetandTrack
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
            self.simwin = Tkinter.Toplevel(self)
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
            self.detwin = Tkinter.Toplevel(self)
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
            self.trackwin = Tkinter.Toplevel(self)
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
            self.dettrackwin = Tkinter.Toplevel(self)
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
            self.anawin = Tkinter.Toplevel(self)
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
        
        simbutton = Tkinter.Button(self, text=u"Simulation",command=runSimulation)
        simbutton.grid(column=0,row=1,sticky="EW")
        detbutton = Tkinter.Button(self, text=u"Detection",command=runDetection)
        detbutton.grid(column=0,row=2,sticky="EW")
        trabutton = Tkinter.Button(self, text=u"Tracking",command=runTracking)
        trabutton.grid(column=0,row=3,sticky="EW")
        detatrabutton = Tkinter.Button(self, text=u"Detect and Track",command=runDetandTrack)
        detatrabutton.grid(column=0,row=4,sticky="EW")
        anabutton = Tkinter.Button(self, text=u"Analysis",command=runAnalysis)
        anabutton.grid(column=0,row=5,sticky="EW")
        exibutton = Tkinter.Button(self, text=u"Quit", command=self.destroy)
        exibutton.grid(column=0,row=6,sticky="EW")
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
