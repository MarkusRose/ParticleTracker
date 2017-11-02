try:
    import tkinter as tk
    import tkinter.filedialog
    import tkinter.messagebox
    import tkinter.ttk
except ImportError:
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk
import sys

import os

import time
import threading
try:
    import queue
except ImportError:
    import queue as Queue

import Detection.det_and_track
import Detection.detectParticles
import tracking
import AnalysisTools.driftCorrection as dc

class guiDetandTrack(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.detMethod = ['Centroid','Local Maximum']
        self.doSetup()
        self.grab_set()
        return


    def doSetup(self):
        self.mainframe = tkinter.ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        tkinter.ttk.Button(self.mainframe, text="Run", command=self.runDetAndTrack).grid(column=2,row=2, sticky="SE")
        tkinter.ttk.Button(self.mainframe, text="Cancel", command=self.parent.destroy).grid(column=2,row=3, sticky='E')
        
        self.labelframe = tkinter.ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)

        self.inImagesVar = tk.StringVar()
        self.inImagesVar.set("Please select Image Folder")
        tkinter.ttk.Button(self.labelframe, text="Input Images", command = lambda:self.inImagesVar.set(tkinter.filedialog.askdirectory())).grid(column=1, row=1, sticky='W')
        tkinter.ttk.Entry(self.labelframe, textvariable = self.inImagesVar).grid(column=2, row=1, sticky='W')

        
        self.dcvar = tk.IntVar()
        self.dcvar.set(0)
        tk.Checkbutton(self.labelframe,text="Drift Correction",variable=self.dcvar).grid(column=1,row=14,sticky='W')
        self.feducialVar = tk.StringVar()
        self.feducialVar.set(os.path.abspath(os.path.join(self.inImagesVar.get(), '..', 'Analysis')))
        tkinter.ttk.Button(self.labelframe, text="Fiducial Markers", command = lambda:self.feducialVar.set(tkinter.filedialog.askdirectory())).grid(column=1, row=15, sticky='W')
        tkinter.ttk.Entry(self.labelframe, textvariable = self.feducialVar).grid(column=2, row=15, sticky='W')

        self.outDirVar = tk.StringVar()
        self.outDirVar.set(os.path.abspath(os.path.join(self.inImagesVar.get(), '..', 'Analysis')))
        tkinter.ttk.Button(self.labelframe, text="Output Folder", command = lambda:self.outDirVar.set(tkinter.filedialog.askdirectory())).grid(column=1, row=13, sticky='W')
        tkinter.ttk.Entry(self.labelframe, textvariable = self.outDirVar).grid(column=2, row=13, sticky='W')

        dependency = ["Sigma", "Signal Power", "Image Bit Depth",
                "Number of Images to add up", "Sigma Threshold",
                "Eccentricity Threshold", "Local maximum window size", 
                "Maximum Displacement", "Minimum Track Length", "Linking Range (frame skip)"] 
        self.vars = []

        for i in range(len(dependency)):
            var = tk.StringVar()
            tkinter.ttk.Label(self.labelframe, text=dependency[i]).grid(column=1, row=2+i, sticky='W')
            tkinter.ttk.Entry(self.labelframe, textvariable = var).grid(column=2, row=2+i, sticky='W')
            self.vars.append(var)

        self.vars[0].set("2")
        self.vars[1].set("3")
        self.vars[2].set("16")
        self.vars[3].set("1")
        self.vars[4].set("2")
        self.vars[5].set("2")
        self.vars[6].set("10")
        self.vars[7].set("5")
        self.vars[8].set("1")
        self.vars[9].set("2")

        self.detMethVar = tk.StringVar()
        self.detMethVar.set(self.detMethod[1])
        tkinter.ttk.Label(self.labelframe, text="Detection Method").grid(column=1, row=11, sticky='W')
        drop = tk.OptionMenu(self.labelframe,self.detMethVar,*(self.detMethod))
        drop.grid(column=2,row=11,sticky="EW")


        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return


    def checkInputs(self):
        try:
            #Input Images Folder exists
            if not os.path.isdir(self.inImagesVar.get()):
                tkinter.messagebox.showerror("No Images", "Images could not be located.")
                return False

            for elem in self.vars:
                if float(elem.get()) <= 0:
                    raise ValueError
            
            #Initial Positions File
            #Output Folder
            if os.path.isdir(self.outDirVar.get()):
                if not tkinter.messagebox.askyesno("Folder Exists!", "This folder exists. Do you want to copy over its content?"):
                    return False
            
        except ValueError:
            tkinter.messagebox.showerror("NaN", "One of the entries is not correct (not a number).")
            return False

        return True

    def variablesToProgram(self):
        outvars = []
        filenames = []
        filenames.append(self.inImagesVar.get())
        filenames.append(self.outDirVar.get())
        filenames.append(self.feducialVar.get())

        for elem in self.vars:
            outvars.append(float(elem.get()))
        if self.detMethVar.get() == self.detMethod[0]:
            outvars.append(0)
        else:
            outvars.append(1)

        return outvars, filenames
            
            
    def runDetAndTrack(self):
        if self.checkInputs():
            outv,fn = self.variablesToProgram()
            top = tk.Toplevel()
            top.title("Detection and Tracking running")
            tk.Message(top, text="Running detection and tracking now. This might take a while.", padx=20, pady=20).pack()
            #System.Fileio.setSysProps(self.giveToProgram())
            
            q = queue.Queue()


            def on_main_thread(func):
                q.put(func)

            def check_queue():
                while True:
                    try:
                        task = q.get(block=False)
                    except queue.Empty:
                        break
                    else:
                        self.after_idle(task)
                self.after(100,check_queue)

            def done_mssg():
                tkinter.messagebox.showinfo("Done!", "Detection and Tracking finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def calculator():
                    images = Detection.det_and_track.readImageList(fn[0])
                    if not os.path.isdir(fn[1]):
                        os.mkdir(fn[1])
                    os.chdir(fn[1])
                    notCentroid = (outv[10] == 1)
                    particle_data = Detection.detectParticles.multiImageDetect(images,outv[0],outv[6],outv[1],outv[2],outv[5],outv[4],int(outv[3]),local_max=None,output=False,lmmethod=notCentroid,imageOutput=False,path=fn[1])
                    if self.dcvar.get():
                        drift_images = Detection.det_and_track.readImageList(fn[2])
                        drift_data = Detection.detectParticles.multiImageDetect(drift_images,outv[0],outv[6],outv[1]+2,outv[2],outv[5],outv[4],int(outv[3]),local_max=None,output=False,lmmethod=notCentroid,imageOutput=False,path=fn[1],pfilename='fiducialMarkers.txt')
                        track_data = dc.track_with_driftcorrect([particle_data,drift_data],searchRadius=outv[7],link_range=outv[9],path=fn[1])
                    else:     
                        track_data = dc.doTrack_direct(particle_data, searchRadius=outv[7],minTracklen=int(outv[8]),linkRange=int(outv[9]),outfile="foundTracks.txt",infilename="Not Defined",path=fn[1])
                    on_main_thread(top.destroy)
                    on_main_thread(done_mssg)
                    on_main_thread(self.parent.destroy)
                t = threading.Thread(target=calculator)
                t.start()
            self.after(1,handle_calc)
            self.after(100,check_queue)
            print("Done")
        else:
            print("Wrong inputs")
        return


if __name__ == "__main__":
    root = tk.Tk(None)
    root.title("Particle Tracker Setup")
    app = guiDetection(root)
    app.pack()
    root.mainloop()

