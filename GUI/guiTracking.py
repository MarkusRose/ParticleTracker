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
import time
import threading
try:
    import Queue as queue
except ImportError:
    import queue 

import tracking
from AnalysisTools import driftCorrection as dc
from skimage import io
from Visualization import imageReader as ir

class guiTracking(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.doSetup()
        self.grab_set()
        return

    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        ttk.Button(self, text="Run", command=self.runTracking).grid(column=1,row=2, sticky="SW")
        ttk.Button(self, text="Cancel", command=self.parent.destroy).grid(column=1,row=3, sticky='SW')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)


        self.inPosVar = tk.StringVar()
        self.inPosVar.set("Please select position file.")
        ttk.Button(self.labelframe, text="Positions File", command = lambda:self.inPosVar.set(filedialog.askopenfilename())).grid(column=1, row=1, sticky='W')
        ttk.Label(self.labelframe,textvariable=self.inPosVar).grid(column=2, row=1, sticky='W')

        
        self.maxDispVar = tk.StringVar()
        self.maxDispVar.set("3")
        ttk.Label(self.labelframe, text="Maximum displacement").grid(column=1, row=2, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.maxDispVar).grid(column=2, row=2, sticky='W')


        self.minTrVar = tk.StringVar()
        self.minTrVar.set('1')
        ttk.Label(self.labelframe, text="Minimum track length").grid(column=1, row=3, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.minTrVar).grid(column=2, row=3, sticky='W')

        self.linkRaVar = tk.StringVar()
        self.linkRaVar.set("2")
        ttk.Label(self.labelframe, text="Link range (frameskip)").grid(column=1, row=4, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.linkRaVar).grid(column=2, row=4, sticky='W')


        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return    


    def checkInputs(self):
        try:
            if not os.path.isfile(self.inPosVar.get()):
                messagebox.showerror("Not a file", "File does not exist. Please choose the correct file!")
                return False
            #Maximum displacement
            if float(self.maxDispVar.get()) <=0 :
                self.maxDispVar.set("2")
                messagebox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to 2px.")
                return False

            #minimum track length
            if int(self.minTrVar.get())<1:
                self.minTrVar.set("1")
                messagebox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to track length of 1.")
                return False

            #link range
            if int(self.linkRaVar.get())<1:
                self.minTrVar.set("1")
                messagebox.showwarning("Reset Value", "Value(s) was/were incorrect. Link range set to 1.")
                return False

            #Initial Positions File
            #Output Folder
            if os.path.isdir(os.path.dirname(self.inPosVar.get())):
                if not messagebox.askyesno("Folder Exists!", "This folder exists. Some content might be lost. Continue?"):
                    return False
        except ValueError:
            messagebox.showerror("NaN", "One of the entries is not correct (not a number).")
            return False

        return True
            
    def varsToProgram(self):
        outlist = []
        outlist.append(self.inPosVar.get())
        outlist.append(float(self.maxDispVar.get()))
        outlist.append(int(self.minTrVar.get()))
        outlist.append(int(self.linkRaVar.get()))
        outlist.append(os.path.dirname(self.inPosVar.get()))
        return outlist

            
    def runTracking(self):
        if self.checkInputs():
            #print "Works now"
            outv = self.varsToProgram()

            top = tk.Toplevel()
            top.title("Tracking running")
            tk.Message(top, text="Tracking now. This might take a while.", padx=20, pady=20).pack()
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
                messagebox.showinfo("Done!", "Tracking finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def calculator():
                    if not os.path.isdir(outv[4]):
                        os.mkdir(outv[4])
                    os.chdir(outv[4])
                    tracks = dc.doTrack(outv[0],searchRadius=outv[1],minTracklen=outv[2],linkRange=outv[3])
                    namelist = []
                    for i in range(len(tracks)):
                        namelist.append(tracks[i].id)
                    on_main_thread(top.destroy)
                    on_main_thread(done_mssg)
                    #on_main_thread(self.parent.destroy)
                    print("Displaying Tracks now.")

                #t = threading.Thread(target=calculator)
                #t.start()
                calculator()
            self.after(1,handle_calc)
            self.after(100,check_queue)
            print("Done")
        else:
            print("Wrong inputs")
        return


    def setFileName(self):
        self.inImagesVar.set(filedialog.askopenfilename())
        return


if __name__ == "__main__":
    root = tk.Tk(None)
    root.title("Particle Tracker Setup")
    app = guiTracking(root)
    app.pack()
    root.mainloop()
