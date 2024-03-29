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
import time
import threading
try:
    import Queue
except ImportError:
    import queue as Queue

import os

import Detection
import AnalysisTools.driftCorrection as dc
from Visualization import imageReader as ir
from skimage import io

class guiDetection(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.detMethod = ['Gaussian Least Squares','Centroid','Radial Symmetry Centers']
        self.doSetup()
        self.grab_set()
        return


    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        ttk.Button(self, text="Preview", command=self.runPreview).grid(column=2,row=1, sticky="SE")

        ttk.Button(self, text="Run", command=self.runDetection).grid(column=2,row=2, sticky="SE")
        ttk.Button(self, text="Cancel", command=self.parent.destroy).grid(column=2,row=3, sticky='E')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)


        self.inImagesVar = tk.StringVar()
        self.inImagesVar.set("Please select Image Folder")
        ttk.Button(self.labelframe, text="Input Images", command = self.setFileName).grid(column=1, row=1, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.inImagesVar).grid(column=2, row=1, sticky='W')

        self.dcvar = tk.IntVar()
        self.dcvar.set(0)
        tk.Checkbutton(self.labelframe,text="Drift Correction",variable=self.dcvar).grid(column=1,row=14,sticky='W')
        self.feducialVar = tk.StringVar()
        self.feducialVar.set("Select Feducial Marker Images")
        ttk.Button(self.labelframe, text="Fiducial Markers", command = lambda:self.feducialVar.set(filedialog.askopenfilename())).grid(column=1, row=15, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.feducialVar).grid(column=2, row=15, sticky='W')

        self.outDirVar = tk.StringVar()
        self.outDirVar.set("Set Output Folder")
        ttk.Button(self.labelframe, text="Output Folder", command = lambda:self.outDirVar.set(filedialog.askdirectory())).grid(column=1, row=13, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.outDirVar).grid(column=2, row=13, sticky='W')

        dependency = ["Sigma", "Signal Power", "Image Bit Depth",
                "Number of Images to add up", "Sigma Threshold",
                "Eccentricity Threshold", "Local maximum window size"] 
        self.vars = []

        for i in range(len(dependency)):
            var = tk.StringVar()
            if i != 3:
                ttk.Label(self.labelframe, text=dependency[i]).grid(column=1, row=2+i, sticky='W')
                ttk.Entry(self.labelframe, textvariable = var).grid(column=2, row=2+i, sticky='W')
            self.vars.append(var)

        self.vars[0].set("2")
        self.vars[1].set("3")
        self.vars[2].set("16")
        self.vars[3].set("1")
        self.vars[4].set("2")
        self.vars[5].set("2")
        self.vars[6].set("10")

        self.detMethVar = tk.StringVar()
        self.detMethVar.set(self.detMethod[0])
        ttk.Label(self.labelframe, text="Detection Method").grid(column=1, row=11, sticky='W')
        drop = tk.OptionMenu(self.labelframe,self.detMethVar,*(self.detMethod))
        drop.grid(column=2,row=11,sticky="EW")


        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return

    def setFileName(self):
        self.inImagesVar.set(filedialog.askopenfilename())
        self.outDirVar.set(os.path.abspath(os.path.join(os.path.dirname(self.inImagesVar.get()), 'Analysis')))
        return

    def checkInputs(self):
        try:
            #Input Image file exists?
            if not os.path.isfile(self.inImagesVar.get()):
                messagebox.showerror("No Images", "Images could not be located.")
                return False

            #Feducial Image file exists?
            #if not os.path.isfile(self.feducialVar.get()):
            #    messagebox.showerror("No Images", "Images could not be located.")
            #    return False

            for elem in self.vars:
                if float(elem.get()) <= 0:
                    raise ValueError
            
            #Initial Positions File
            #Output Folder
            '''
            if os.path.isdir(self.outDirVar.get()):
                if not messagebox.askyesno("Folder Exists!", "This folder exists. Do you want to copy over its content?"):
                    return False
                    '''
            
        except ValueError:
            messagebox.showerror("NaN", "One of the entries is not correct (not a number).")
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
        if self.detMethVar.get() == self.detMethod[2]:
            outvars.append('radial_center')
        elif self.detMethVar.get() == self.detMethod[1]:
            outvars.append('centroid')
        else:
            outvars.append('gaussian')

        return outvars, filenames

            
    def runDetection(self):
        if self.checkInputs():
            outv,fn = self.variablesToProgram()
            top = tk.Toplevel()
            top.title("Detection running")
            tk.Message(top, text="Running detection now. This might take a while.", padx=20, pady=20).pack()
            #System.Fileio.setSysProps(self.giveToProgram())
            
            q = Queue.Queue()
            def on_main_thread(func):
                q.put(func)

            def check_queue():
                while True:
                    try:
                        task = q.get(block=False)
                    except Queue.Empty:
                        break
                    else:
                        self.after_idle(task)
                self.after(100,check_queue)

            def done_mssg():
                messagebox.showinfo("Done!", "Detection finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def calculator():
                    images = io.imread(fn[0])
                    if not os.path.isdir(fn[1]):
                        os.mkdir(fn[1])
                    notCentroid = (outv[-1] == 1)
                    particle_data = Detection.detectParticles.multiImageDetect(images,outv[0],
                            outv[6],outv[1],outv[2],outv[5],outv[4],int(outv[3]),
                            local_max=None,output=False,method=outv[7],
                            imageOutput=False,path=fn[1])
                    if self.dcvar.get():
                        print("True")
                        sys.stdout.flush()
                        drift_images= io.imread(fn[2])
                        drift_data = Detection.detectParticles.multiImageDetect(drift_images,
                                outv[0],outv[6],outv[1]+2,outv[2],outv[5],outv[4],
                                int(outv[3]),local_max=None,output=False,method=outv[7],
                                imageOutput=False,path=fn[1])
                        particle_data = dc.position_with_driftcorrect([particle_data,drift_data],path=fn[1])

                    ir.showDetections(images,particle_data)
                    on_main_thread(top.destroy)
                    on_main_thread(done_mssg)
                    #on_main_thread(self.parent.destroy)
                #t = threading.Thread(target=calculator)
                #t.start()
                calculator()
            self.after(1,handle_calc)
            self.after(100,check_queue)
            print("Done")
        else:
            print("Wrong inputs")
        return

    def runPreview(self):
        if self.checkInputs():
            outv,fn = self.variablesToProgram()

            def handle_calc():
                images = io.imread(fn[0])
                if not os.path.isdir(fn[1]):
                    os.mkdir(fn[1])
                notCentroid = (outv[-1] == 1)
                particle_data = Detection.detectParticles.previewImageDetect(images[:1],
                        outv[0],
                        outv[6],outv[1],outv[2],outv[5],outv[4],int(outv[3]),
                        local_max=None,output=False,method=outv[-1],
                        imageOutput=False,path=fn[1])
                ir.showDetections(images[0:1],particle_data)
            self.after(1,handle_calc)
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

