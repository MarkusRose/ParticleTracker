try:
    import Tkinter as tk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
except ImportError:
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk

import System.Fileio
import Simulation.enzymeDiffuser
import time
import threading
try: 
    import Queue as queue
except ImportError:
    import queue
import os
import sys

class Simulation_App(tk.Frame):
    

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.initVars()
        self.initialyze()
        self.grab_set()
        return

    
    def initVars(self):
        self.diff1Var = tk.StringVar()
        self.diff2Var = tk.StringVar()
        self.diff3Var = tk.StringVar()
        self.diff1Var.set("3.0")
        self.diff2Var.set("n/a")
        self.diff3Var.set("n/a")
        self.prob12 = tk.StringVar()
        self.prob21 = tk.StringVar()
        self.prob13 = tk.StringVar()
        self.prob31 = tk.StringVar()
        self.prob23 = tk.StringVar()
        self.prob32 = tk.StringVar()
        self.prob12.set("0.0")
        self.prob21.set("1.0")
        self.prob13.set("0.0")
        self.prob23.set("0.0")
        self.prob31.set("1.0")
        self.prob32.set("0.0")
        self.numframesVar = tk.StringVar()
        self.numframesVar.set("10")
        self.numPartVar = tk.StringVar()
        self.numPartVar.set("10")
        self.tauVar = tk.StringVar()
        self.tauVar.set("0.06")
        self.frameLengthVar = tk.StringVar()
        self.frameLengthVar.set("512")
        self.lambdaVar = tk.StringVar()
        self.lambdaVar.set("700")
        self.pixsizeVar = tk.StringVar()
        self.pixsizeVar.set("0.1")
        self.naVar = tk.StringVar()
        self.naVar.set("1.45")
        self.backgroundVar = tk.StringVar()
        self.backgroundVar.set("300")
        self.backnoiseVar = tk.StringVar()
        self.backnoiseVar.set("100")
        self.intensityVar = tk.StringVar()
        self.intensityVar.set("3000")
        self.saveDir = tk.StringVar()
        self.saveDir.set(".")

    def checkVars(self):
        try:
            #Check diff Constants and number of states
            if int(self.numStates.get()) >=3:
                if (self.diff3Var.get() == "n/a" or float(self.diff3Var.get()) < 0):
                    messagebox.showerror("D3 false", "Third Diffusion coefficient does not match!")
                    return False
                if ((self.prob13.get() == "0.0" or float(self.prob13.get()) <=0 or float(self.prob13.get()) >=1) or
                    (self.prob23.get() == "0.0" or float(self.prob23.get()) <=0 or float(self.prob23.get()) >=1) or
                    (self.prob31.get() == "0.0" or float(self.prob31.get()) <=0 or float(self.prob31.get()) >=1) or
                    (self.prob32.get() == "0.0" or float(self.prob32.get()) <=0 or float(self.prob32.get()) >=1)):
                    messagebox.showerror("Probs false", "Transition probatilities concerning the third diffusion coefficient do not match number of states!")
                    return False
            if int(self.numStates.get()) >=2:
                if (self.diff2Var.get() == "n/a" or float(self.diff2Var.get()) < 0):
                    messagebox.showerror("D2 false", "Second Diffusion coefficient does not match!")
                    return False
                if ((self.prob12.get() == "0.0" or float(self.prob12.get()) <=0 or float(self.prob12.get()) >=1) or
                    (self.prob21.get() == "0.0" or float(self.prob21.get()) <=0 or float(self.prob21.get()) >=1)):
                    messagebox.showerror("Probs false", "Transition probatilities concerning the first and second diffusion coefficient do not match number of states!")
                    return False
            if (len(self.diff1Var.get()) == 0 or float(self.diff1Var.get()) < 0):
                messagebox.showerror("D1 false", "First Diffusion coefficient does not match!")
                return False
            if int(self.numStates.get()) == 2:
                self.diff3Var.set("0.0")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("0.0")
                self.prob32.set("0.0")
            
            if int(self.numStates.get()) == 1:
                self.diff2Var.set("0.0")
                self.diff3Var.set("0.0")
                self.prob12.set("0.0")
                self.prob21.set("1.0")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("1.0")
                self.prob32.set("0.0")
            
            #Check number of frames, particles
            if int(self.numframesVar.get()) < 1:
                messagebox.showerror("Wrong Framenumber", "Number of Frames must be larger than 0.")
                return False
            if int(self.numPartVar.get()) < 1:
                messagebox.showerror("Wrong Particle Number", "Number of particles must be larger than 0!")
                return False
            
            #Test wavelength, acquisition time, NA
            if float(self.tauVar.get()) <= 0:
                messagebox.showerror("A.Time","Acquisition time has to be larger than 0.")
                return False
            if float(self.lambdaVar.get()) <= 0:
                messagebox.showerror("Wavelength", "Wavelength must be larger than 0.")
                return False
            if float(self.naVar.get()) <=0:
                messagebox.showerror("NA","Numerical aperture must be larger than 0.")
                return False

            #Image properties: frame length, pixel size, signal to noise, intensity
            if int(self.frameLengthVar.get()) <= 1:
                messagebox.showerror("# of Pixels", "Number of Pixels must be larger than 1.")
                return False
            if float(self.pixsizeVar.get()) <= 0:
                messagebox.showerror("Pixel size", "Pixels must have a size larget than 0.")
                return False
            if float(self.backgroundVar.get()) < 0:
                messagebox.showerror("Background", "Background cannot be negative.")
                return False
            if float(self.backnoiseVar.get()) <= 0:
                messagebox.showerror("Background noise", "Background noise must be larger than 0.")
                return False
            if float(self.intensityVar.get()) <= 0:
                messagebox.showerror("Intensity", "Intensity must be larger than 0.")
        except ValueError:
            messagebox.showerror("NaN","Some entry is not a number!")
            return False
        
        return True
            
    
    def initialyze(self):
        self.grid()
        
        #All text inputs
        #Number of States
        numStatesLabel = tk.Label(self, text="Number of States")
        numStatesLabel.grid(column=0,row=0,sticky="EW")
        self.numStates= tk.Spinbox(self, from_=1, to=3)
        self.numStates.grid(column=1,row=0,sticky="EW")
        #Diffconsts
        diffFrame = tk.Frame(self)
        numDiffButton = tk.Button(diffFrame, text="Set Diff.Const.", command=self.setDiffs)
        numDiffButton.grid(column=0,row=0, sticky="EW")
        l1 = tk.Label(diffFrame,text="D1 = ")
        l1.grid(column = 1, row = 0)
        d1 = tk.Label(diffFrame,textvariable=self.diff1Var)
        d1.grid(column = 2, row = 0)
        l1l = tk.Label(diffFrame,text=" um^2/s")
        l1l.grid(column = 3, row = 0, sticky = "E")
        l2 = tk.Label(diffFrame,text="D2 = ")
        l2.grid(column = 1, row = 1)
        d2 = tk.Label(diffFrame,textvariable=self.diff2Var)
        d2.grid(column = 2, row = 1)
        l2l = tk.Label(diffFrame,text=" um^2/s")
        l2l.grid(column = 3, row = 1, sticky = "E")
        l3 = tk.Label(diffFrame,text="D3 = ")
        l3.grid(column = 1, row = 2)
        d3 = tk.Label(diffFrame,textvariable=self.diff3Var)
        d3.grid(column = 2, row = 2)
        l3l = tk.Label(diffFrame,text=" um^2/s")
        l3l.grid(column = 3, row = 2, sticky ="E")

        d12l = tk.Label(diffFrame,text="p12 = ")
        d12l.grid(column=4, row=0)
        d21l = tk.Label(diffFrame,text="p21 = ")
        d21l.grid(column=4, row=1)
        d13l = tk.Label(diffFrame,text="p13 = ")
        d13l.grid(column=4, row=2)
        d23l = tk.Label(diffFrame,text="p23 = ")
        d23l.grid(column=6, row=0)
        d31l = tk.Label(diffFrame,text="p31 = ")
        d31l.grid(column=6, row=1)
        d32l = tk.Label(diffFrame,text="p32 = ")
        d32l.grid(column=6, row=2)
        d12 = tk.Label(diffFrame, textvariable=self.prob12)
        d12.grid(column=5, row=0)
        d21 = tk.Label(diffFrame, textvariable=self.prob21)
        d21.grid(column=5, row=1)
        d13 = tk.Label(diffFrame, textvariable=self.prob13)
        d13.grid(column=5, row=2)
        d23 = tk.Label(diffFrame, textvariable=self.prob23)
        d23.grid(column=7, row=0)
        d31 = tk.Label(diffFrame, textvariable=self.prob31)
        d31.grid(column=7, row=1)
        d32 = tk.Label(diffFrame, textvariable=self.prob32)
        d32.grid(column=7, row=2)
        diffFrame.grid(column=0,row=1,rowspan=1, columnspan=3, sticky="EW")
        diffFrame.grid_columnconfigure(2,weight=1)
        diffFrame.grid_columnconfigure(5,weight=1)
        diffFrame.grid_columnconfigure(7,weight=1)

        
        #Number of frames
        numframesLabel = tk.Label(self, text="Number of Frames")
        numframesLabel.grid(column=0,row=4,sticky="EW")
        numframesText = tk.Entry(self, textvariable=self.numframesVar)
        numframesText.grid(column=1,row=4, sticky="EW")
        #Number of Particles
        numPartLabel = tk.Label(self, text="Number of Particles")
        numPartLabel.grid(column=0,row=5,sticky="EW")
        numPartText = tk.Entry(self, textvariable=self.numPartVar)
        numPartText.grid(column=1,row=5, sticky="EW")
        #Acquisition time
        tauLabel = tk.Label(self,text="Acquisition Time [s]")
        tauLabel.grid(column=0,row=6,sticky="EW")
        tauText = tk.Entry(self, textvariable=self.tauVar)
        tauText.grid(column=1,row=6, sticky="EW")
        #Frame dimension a (a x a pixels)
        frameLengthLabel = tk.Label(self,text="Frame height and width [pixels]")
        frameLengthLabel.grid(column=0,row=7,sticky="EW")
        frameLengthText = tk.Entry(self, textvariable=self.frameLengthVar)
        frameLengthText.grid(column=1,row=7, sticky="EW")
        #Wavelength
        lambdaLabel = tk.Label(self,text="Wavelength [nm]")
        lambdaLabel.grid(column=0,row=8,sticky="EW")
        lambdaText = tk.Entry(self, textvariable=self.lambdaVar)
        lambdaText.grid(column=1,row=8, sticky="EW")
        #Pixelsize
        pixsizeLabel = tk.Label(self,text="Pixelsize [um]")
        pixsizeLabel.grid(column=0,row=9,sticky="EW")
        pixsizeText = tk.Entry(self, textvariable=self.pixsizeVar)
        pixsizeText.grid(column=1,row=9, sticky="EW")
        #NA
        naLabel = tk.Label(self,text="Numerical Aperture")
        naLabel.grid(column=0,row=10,sticky="EW")
        naText = tk.Entry(self, textvariable=self.naVar)
        naText.grid(column=1,row=10, sticky="EW")
        #Background
        backgroundLabel = tk.Label(self,text="Background mean")
        backgroundLabel.grid(column=0,row=12,sticky="EW")
        backgroundText = tk.Entry(self, textvariable=self.backgroundVar)
        backgroundText.grid(column=1,row=12, sticky="EW")
        #Background noise
        backnoiseLabel = tk.Label(self,text="Background noise")
        backnoiseLabel.grid(column=0,row=13,sticky="EW")
        backnoiseText = tk.Entry(self, textvariable=self.backnoiseVar)
        backnoiseText.grid(column=1,row=13, sticky="EW")
        #Intensity
        intensityLabel = tk.Label(self,text="Intensity")
        intensityLabel.grid(column=0,row=14,sticky="EW")
        intensityText = tk.Entry(self, textvariable=self.intensityVar)
        intensityText.grid(column=1,row=14, sticky="EW")

    
        #output directory location
        dirButton = tk.Button(self, text="Output Location", command = lambda:self.saveDir.set(filedialog.askdirectory()))
        dirButton.grid(column=0, row=15, sticky='W')
        directoryLabel = tk.Entry(self,textvariable=self.saveDir)
        directoryLabel.grid(column=1,row=15)


        #Save settings and run simulation or cancel with buttons
        runButton = tk.Button(self, text="Save & Run", command=self.runcomm)
        runButton.grid(column=2,row=12, sticky="EW")
        cancelButton = tk.Button(self, text="Cancel", command=self.parent.destroy)
        cancelButton.grid(column=2,row=13, sticky="EW")

        self.grid_columnconfigure(1,weight=1)
        

    def setDiffs(self):
        fra = tk.Toplevel(self)
        fra.wm_title("Diffusion Constants")
        fra.grid()
        #D1
        diff1Label = tk.Label(fra, text="Diff const 1 [um^2/s]")
        diff1Label.grid(column=0,row=1,sticky="EW")
        diff1Text = tk.Entry(fra, textvariable=self.diff1Var)
        diff1Text.grid(column=1,row=1,sticky="EW")
        if int(self.numStates.get()) >=2:
            #D2
            diff2Label = tk.Label(fra, text="Diff const 2 [um^2/s]")
            diff2Label.grid(column=0,row=2,sticky="EW")
            diff2Text = tk.Entry(fra, textvariable=self.diff2Var)
            diff2Text.grid(column=1,row=2, sticky="EW")
            prob12Label = tk.Label(fra, text="p1->2 = ")
            prob12Label.grid(column=2,row=1,sticky="EW")
            prob21Label = tk.Label(fra, text="p2->1 = ")
            prob21Label.grid(column=2,row=2,sticky="EW")
            prob12Text = tk.Entry(fra, textvariable=self.prob12)
            prob12Text.grid(column=3,row=1,sticky="EW")
            prob21Label = tk.Label(fra, text="p2->1 = ")
            prob21Label.grid(column=2,row=2,sticky="EW")
            prob21Text = tk.Entry(fra, textvariable=self.prob21)
            prob21Text.grid(column=3,row=2,sticky="EW")
            if int(self.numStates.get()) >=3:
                #D3
                diff3Label = tk.Label(fra, text="Diff const 3 [um^2/s]")
                diff3Label.grid(column=0,row=3,sticky="EW")
                diff3Text = tk.Entry(fra, textvariable=self.diff3Var)
                diff3Text.grid(column=1,row=3, sticky="EW")
                prob13Label = tk.Label(fra, text="p1->3 = ")
                prob13Label.grid(column=2,row=3,sticky="EW")
                prob13Text = tk.Entry(fra, textvariable=self.prob13)
                prob13Text.grid(column=3,row=3,sticky="EW")
                prob23Label = tk.Label(fra, text="p2->3 = ")
                prob23Label.grid(column=2,row=4,sticky="EW")
                prob23Text = tk.Entry(fra, textvariable=self.prob23)
                prob23Text.grid(column=3,row=4,sticky="EW")
                prob31Label = tk.Label(fra, text="p3->1 = ")
                prob31Label.grid(column=2,row=5,sticky="EW")
                prob31Text = tk.Entry(fra, textvariable=self.prob31)
                prob31Text.grid(column=3,row=5,sticky="EW")
                prob32Label = tk.Label(fra, text="p3->2 = ")
                prob32Label.grid(column=2,row=6,sticky="EW")
                prob32Text = tk.Entry(fra, textvariable=self.prob32)
                prob32Text.grid(column=3,row=6,sticky="EW")
            else:
                self.diff3Var.set("0.0")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("0.0")
                self.prob32.set("0.0")
        else:
            self.diff2Var.set("0.0")
            self.prob12.set("0.0")
            self.prob21.set("1.0")
            self.prob13.set("0.0")
            self.prob23.set("0.0")
            self.prob31.set("1.0")
            self.prob32.set("0.0")

        def saveDiffs():
            fra.destroy()
        
        closeButton = tk.Button(fra, text="Close", command=saveDiffs)
        closeButton.grid(column=1,row=7)

        fra.mainloop()

    def giveToProgram(self):
        outvar = []
        outvar.append(int(self.numStates.get()))
        outvar.append(float(self.diff1Var.get()))
        outvar.append(float(self.diff2Var.get()))
        outvar.append(float(self.diff3Var.get())) 
        outvar.append(float(self.prob12.get())) 
        outvar.append(float(self.prob21.get())) 
        outvar.append(float(self.prob13.get())) 
        outvar.append(float(self.prob23.get())) 
        outvar.append(float(self.prob31.get())) 
        outvar.append(float(self.prob32.get())) 
        outvar.append(float(self.numframesVar.get())) 
        outvar.append(float(self.numPartVar.get())) 
        outvar.append(float(self.tauVar.get())) 
        outvar.append(float(self.frameLengthVar.get())) 
        outvar.append(float(self.lambdaVar.get())) 
        outvar.append(float(self.pixsizeVar.get())) 
        outvar.append(float(self.naVar.get())) 
        outvar.append(float(self.backgroundVar.get()))
        outvar.append(float(self.backnoiseVar.get()))
        outvar.append(float(self.intensityVar.get())) 
        directory = str(self.saveDir.get())
        return outvar,directory

        
    def runcomm(self):
        print(">>>>Starting Simulation")
        if self.checkVars():
            print("Everythings fine, running program now. Have to pass variables to Fileio.setSysProps with all the parameters given.")
            top = tk.Toplevel(self)
            top.title("Simulation running")
            top.grab_set()
            tk.Message(top, text="Running simulation now. This might take a while.", padx=20, pady=20).pack()
            #System.Fileio.setSysProps(self.giveToProgram())
            outvariable = self.giveToProgram()
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
                top.grab_release()
                messagebox.showinfo("Done!", "Simulation finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def run_sim():
                    print("starting simulation")
                    sys.stdout.flush()
                    Simulation.enzymeDiffuser.simulateTracks(outvariable[0],outvariable[1])
                    print(">>>>Finished Simulation")
                    sys.stdout.flush()
                    on_main_thread(top.destroy)
                    on_main_thread(done_mssg)
                    on_main_thread(self.parent.destroy)
                t = threading.Thread(target=run_sim)
                t.start()
                #run_sim()
            self.after(1,handle_calc)
            self.after(100,check_queue)
            print("Done")
        return


if __name__ == "__main__":
    root = tk.Tk(None)
    app = Simulation_App(root)
    app.pack()
    root.mainloop()
