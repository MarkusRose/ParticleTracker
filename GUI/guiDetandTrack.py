import Tkinter
import ttk
import tkFileDialog
import tkMessageBox
import sys

import os

import time
import threading
import Queue

import Detection.det_and_track
import Detection.detectParticles
import tracking

class guiDetandTrack(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self,parent)
        self.parent = parent
        self.detMethod = ['Centroid','Local Maximum']
        self.doSetup()
        return


    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        ttk.Button(self, text="Run", command=self.runDetAndTrack).grid(column=2,row=2, sticky="SE")
        ttk.Button(self, text="Cancel", command=self.parent.destroy).grid(column=2,row=3, sticky='E')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)

        self.inImagesVar = Tkinter.StringVar()
        self.inImagesVar.set("Please select Image Folder")
        ttk.Button(self.labelframe, text="Input Images", command = lambda:self.inImagesVar.set(tkFileDialog.askdirectory())).grid(column=1, row=1, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.inImagesVar).grid(column=2, row=1, sticky='W')

        self.outDirVar = Tkinter.StringVar()
        self.outDirVar.set(os.path.abspath(os.path.join(self.inImagesVar.get(), '..', 'Analysis')))
        ttk.Button(self.labelframe, text="Output Folder", command = lambda:self.outDirVar.set(tkFileDialog.askdirectory())).grid(column=1, row=13, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.outDirVar).grid(column=2, row=13, sticky='W')

        dependency = ["Sigma", "Signal Power", "Image Bit Depth",
                "Number of Images to add up", "Sigma Threshold",
                "Eccentricity Threshold", "Local maximum window size", 
                "Maximum Displacement", "Minimum Track Length", "Linking Range (frame skip)"] 
        self.vars = []

        for i in xrange(len(dependency)):
            var = Tkinter.StringVar()
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
        self.vars[7].set("5")
        self.vars[8].set("1")
        self.vars[9].set("2")

        self.detMethVar = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Detection Method").grid(column=1, row=11, sticky='W')
        drop = Tkinter.OptionMenu(self.labelframe,self.detMethVar,*(self.detMethod))
        drop.grid(column=2,row=11,sticky="EW")


        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return


    def checkInputs(self):
        try:
            #Input Images Folder exists
            if not os.path.isdir(self.inImagesVar.get()):
                tkMessageBox.showerror("No Images", "Images could not be located.")
                return False

            for elem in self.vars:
                if float(elem.get()) <= 0:
                    raise ValueError
            
            #Initial Positions File
            #Output Folder
            if os.path.isdir(self.outDirVar.get()):
                if not tkMessageBox.askyesno("Folder Exists!", "This folder exists. Do you want to copy over its content?"):
                    return False
            
        except ValueError:
            tkMessageBox.showerror("NaN", "One of the entries is not correct (not a number).")
            return False

        return True

    def variablesToProgram(self):
        outvars = []
        filenames = []
        filenames.append(self.inImagesVar.get())
        filenames.append(self.outDirVar.get())

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
            top = Tkinter.Toplevel()
            top.title("Detection and Tracking running")
            Tkinter.Message(top, text="Running detection and tracking now. This might take a while.", padx=20, pady=20).pack()
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
                tkMessageBox.showinfo("Done!", "Detection and Tracking finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def calculator():
                    images = Detection.det_and_track.readImageList(fn[0])
                    if not os.path.isdir(fn[1]):
                        os.mkdir(fn[1])
                    os.chdir(fn[1])
                    notCentroid = (outv[10] == 1)
                    particle_data = Detection.detectParticles.multiImageDetect(images,outv[0],outv[6],outv[1],outv[2],outv[5],outv[4],int(outv[3]),local_max=None,output=False,lmmethod=notCentroid,imageOutput=False)
                    tracking.doTrack_direct(particle_data, searchRadius=outv[7],minTracklen=int(outv[8]),linkRange=int(outv[9]),outfile="foundTracks.txt",infilename="Not Defined")
                    on_main_thread(top.destroy)
                    on_main_thread(done_mssg)
                    on_main_thread(self.parent.destroy)
                t = threading.Thread(target=calculator)
                t.start()
            self.after(1,handle_calc)
            self.after(100,check_queue)
            print "Done"
        else:
            print "Wrong inputs"
        return


if __name__ == "__main__":
    root = Tkinter.Tk(None)
    root.title("Particle Tracker Setup")
    app = guiDetection(root)
    app.pack()
    root.mainloop()

