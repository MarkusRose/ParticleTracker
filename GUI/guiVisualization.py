
try:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
except ImportError:
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk
import sys
import os
from skimage import io

from Visualization import imageReader as ir
from Detection import ctrack
from Detection import convertFiles as cf


class guiVisualization(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.doSetup()
        self.grab_set()
        return

    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        ttk.Button(self, text="Show", command=self.runShow).grid(column=1,row=2, sticky="SW")
        ttk.Button(self, text="Cancel", command=self.parent.destroy).grid(column=1,row=3, sticky='SW')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)

        self.inImagesVar = tk.StringVar()
        self.inImagesVar.set("Select Images")
        ttk.Button(self.labelframe, text="Input Images", command = self.setFileName).grid(column=1, row=0, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.inImagesVar).grid(column=2, row=0, sticky='W')


        self.inPosVar = tk.StringVar()
        self.inPosVar.set("Please select position file.")
        ttk.Button(self.labelframe, text="Positions File", command = lambda:self.inPosVar.set(filedialog.askopenfilename())).grid(column=1, row=1, sticky='W')
        ttk.Label(self.labelframe,textvariable=self.inPosVar).grid(column=2, row=1, sticky='W')

        
        self.inTrackVar = tk.StringVar()
        self.inTrackVar.set("Please select track file.")
        ttk.Button(self.labelframe, text="Tracks File", command = lambda:self.inTrackVar.set(filedialog.askopenfilename())).grid(column=1, row=2, sticky='W')
        ttk.Label(self.labelframe,textvariable=self.inTrackVar).grid(column=2, row=2, sticky='W')

        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return    


    def setFileName(self):
        self.inImagesVar.set(filedialog.askopenfilename())
        return

    def varsToProgram(self):
        outlist = []
        state = 0
        if not os.path.isfile(self.inImagesVar.get()):
            messagebox.showwarning("No Images", "Images could not be located.")
            inim = []
        else:
            state += 1
            inim = io.imread(self.inImagesVar.get())
        if not os.path.isfile(self.inPosVar.get()):
            messagebox.showwarning("Not a file", "Position file does not exist. Please choose the correct file!")
            parts = []
        else:
            state += 2
            parts = cf.readDetectedParticles(self.inPosVar.get())
        if not os.path.isfile(self.inTrackVar.get()):
            messagebox.showwarning("Not a file", "Track file does not exist. Please choose the correct file!")
            tracks = []
        else:
            state += 4
            tracks = ctrack.readTrajectoriesFromFile(self.inTrackVar.get())

        return inim,parts,tracks,state


    def runShow(self):
        inim,parts,tracks,state = self.varsToProgram()
        if state == 1:
            ir.showImages(inim)
        elif state == 3:
            ir.showDetections(inim,parts)
        elif state == 5:
            ir.showTracks(inim,tracks)
        elif state == 7:
            ir.showDetections(inim,parts)
            ir.showTracks(inim,tracks)
        elif state % 2 == 0:
            messagebox.showerror("No Images", "No image file specified!")
            return
        else:
            messagebox.showerror("Wrong Input", "This should not have happened!")
            return
        return

if __name__=="__main__":
    app = tk.Tk()

    wind = guiVisualization(parent=app)
    wind.pack()

    app.mainloop()
