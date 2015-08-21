import Tkinter
import tkMessageBox

class Simulation_App(Tkinter.Frame):
    

    def __init__(self,parent):
        Tkinter.Frame.__init__(self,parent)
        self.parent = parent
        self.initVars()
        self.initialyze()

    
    def initVars(self):
        self.diff1Var = Tkinter.StringVar()
        self.diff2Var = Tkinter.StringVar()
        self.diff3Var = Tkinter.StringVar()
        self.diff1Var.set("3.0")
        self.diff2Var.set("")
        self.diff3Var.set("")
        self.numframesVar = Tkinter.StringVar()
        self.numframesVar.set("100")
        self.numPartVar = Tkinter.StringVar()
        self.numPartVar.set("1")
        self.tauVar = Tkinter.StringVar()
        self.tauVar.set("0.1")
        self.frameLengthVar = Tkinter.StringVar()
        self.frameLengthVar.set("512")
        self.lambdaVar = Tkinter.StringVar()
        self.lambdaVar.set("700")
        self.pixsizeVar = Tkinter.StringVar()
        self.pixsizeVar.set("16")
        self.naVar = Tkinter.StringVar()
        self.naVar.set("1.45")
        self.magnifVar = Tkinter.StringVar()
        self.magnifVar.set("100")
        self.signoiseVar = Tkinter.StringVar()
        self.signoiseVar.set("3")
        self.intensityVar = Tkinter.StringVar()
        self.intensityVar.set("10000")

    def checkVars(self):
        try:
            #Check diff Constants and number of states
            if int(self.numStates.get()) >=3 and (len(self.diff3Var.get()) == 0 or float(self.diff3Var.get()) < 0):
                tkMessageBox.showerror("D3 false", "Third Diffusion coefficient does not match!")
                return False
            if int(self.numStates.get()) >=2 and (len(self.diff2Var.get()) == 0 or float(self.diff2Var.get()) < 0):
                tkMessageBox.showerror("D2 false", "Second Diffusion coefficient does not match!")
                return False
            if (len(self.diff1Var.get()) == 0 or float(self.diff1Var.get()) < 0):
                tkMessageBox.showerror("D1 false", "First Diffusion coefficient does not match!")
                return False
            
            #Check number of frames, particles
            if int(self.numframesVar.get()) < 1:
                tkMessageBox.showerror("Wrong Framenumber", "Number of Frames must be larger than 0.")
                return False
            if int(self.numPartVar.get()) < 1:
                tkMessageBox.showerror("Wrong Particle Number", "Number of particles must be larger than 0!")
                return False
            
            #Test wavelength, acquisition time, NA, magnification
            if float(self.tauVar.get()) <= 0:
                tkMessageBox.showerror("A.Time","Acquisition time has to be larger than 0.")
                return False
            if float(self.lambdaVar.get()) <= 0:
                tkMessageBox.showerror("Wavelength", "Wavelength must be larger than 0.")
                return False
            if float(self.naVar.get()) <=0:
                tkMessageBox.showerror("NA","Numerical aperture must be larger than 0.")
                return False
            if float(self.magnifVar.get()) <= 0:
                tkMessageBox.showerror("Magnification", "Magnification must be larger than 0.")
                return False

            #Image properties: frame length, pixel size, signal to noise, intensity
            if int(self.frameLengthVar.get()) <= 1:
                tkMessageBox.showerror("# of Pixels", "Number of Pixels must be larger than 1.")
                return False
            if float(self.pixsizeVar.get()) <= 0:
                tkMessageBox.showerror("Pixel size", "Pixels must have a size larget than 0.")
                return False
            if float(self.signoiseVar.get()) <= 0:
                tkMessageBox.showerror("S/N", "Signal-to-noise must be larger than 0.")
                return False
            if float(self.intensityVar.get()) <= 0:
                tkMessageBox.showerror("Intensity", "Intensity must be larger than 0.")
        except ValueError:
            tkMessageBox.showerror("NaN","Some entry is not a number!")
            return False
        
        return True
            
    
    def initialyze(self):
        self.grid()
        
        #All text inputs
        #Number of States
        numStatesLabel = Tkinter.Label(self, text=u"Number of States")
        numStatesLabel.grid(column=0,row=0,sticky="EW")
        self.numStates= Tkinter.Spinbox(self, from_=1, to=3)
        self.numStates.grid(column=1,row=0,sticky="EW")
        #Diffconsts
        numDiffButton = Tkinter.Button(self, text=u"Set Diff.Const.", command=self.setDiffs)
        numDiffButton.grid(column=0,row=1, sticky="EW")
        diffFrame = Tkinter.Frame(self)
        l1 = Tkinter.Label(diffFrame,text="D1 = ")
        l1.grid(column = 0, row = 0)
        d1 = Tkinter.Label(diffFrame,textvariable=self.diff1Var)
        d1.grid(column = 1, row = 0)
        l1l = Tkinter.Label(diffFrame,text=" um^2/s")
        l1l.grid(column = 2, row = 0, sticky = "E")
        l2 = Tkinter.Label(diffFrame,text="D2 = ")
        l2.grid(column = 0, row = 1)
        d2 = Tkinter.Label(diffFrame,textvariable=self.diff2Var)
        d2.grid(column = 1, row = 1)
        l2l = Tkinter.Label(diffFrame,text=" um^2/s")
        l2l.grid(column = 2, row = 1, sticky = "E")
        l3 = Tkinter.Label(diffFrame,text="D3 = ")
        l3.grid(column = 0, row = 2)
        d3 = Tkinter.Label(diffFrame,textvariable=self.diff3Var)
        d3.grid(column = 1, row = 2)
        l3l = Tkinter.Label(diffFrame,text=" um^2/s")
        l3l.grid(column = 2, row = 2, sticky ="E")
        diffFrame.grid(column=1,row=1,rowspan=1, columnspan=1, sticky="EW")
        diffFrame.grid_columnconfigure(1,weight=1)

        
        #Number of frames
        numframesLabel = Tkinter.Label(self, text=u"Number of Frames")
        numframesLabel.grid(column=0,row=4,sticky="EW")
        numframesText = Tkinter.Entry(self, textvariable=self.numframesVar)
        numframesText.grid(column=1,row=4, sticky="EW")
        #Number of Particles
        numPartLabel = Tkinter.Label(self, text=u"Number of Particles")
        numPartLabel.grid(column=0,row=5,sticky="EW")
        numPartText = Tkinter.Entry(self, textvariable=self.numPartVar)
        numPartText.grid(column=1,row=5, sticky="EW")
        #Acquisition time
        tauLabel = Tkinter.Label(self,text=u"Acquisition Time [s]")
        tauLabel.grid(column=0,row=6,sticky="EW")
        tauText = Tkinter.Entry(self, textvariable=self.tauVar)
        tauText.grid(column=1,row=6, sticky="EW")
        #Frame dimension a (a x a pixels)
        frameLengthLabel = Tkinter.Label(self,text=u"Frame height and width [pixels]")
        frameLengthLabel.grid(column=0,row=7,sticky="EW")
        frameLengthText = Tkinter.Entry(self, textvariable=self.frameLengthVar)
        frameLengthText.grid(column=1,row=7, sticky="EW")
        #Wavelength
        lambdaLabel = Tkinter.Label(self,text=u"Wavelength [nm]")
        lambdaLabel.grid(column=0,row=8,sticky="EW")
        lambdaText = Tkinter.Entry(self, textvariable=self.lambdaVar)
        lambdaText.grid(column=1,row=8, sticky="EW")
        #Pixelsize
        pixsizeLabel = Tkinter.Label(self,text=u"Pixelsize [um]")
        pixsizeLabel.grid(column=0,row=9,sticky="EW")
        pixsizeText = Tkinter.Entry(self, textvariable=self.pixsizeVar)
        pixsizeText.grid(column=1,row=9, sticky="EW")
        #NA
        naLabel = Tkinter.Label(self,text=u"Numerical Aperture")
        naLabel.grid(column=0,row=10,sticky="EW")
        naText = Tkinter.Entry(self, textvariable=self.naVar)
        naText.grid(column=1,row=10, sticky="EW")
        #Magnification
        magnifLabel = Tkinter.Label(self,text=u"Magnification")
        magnifLabel.grid(column=0,row=11,sticky="EW")
        magnifText = Tkinter.Entry(self, textvariable=self.magnifVar)
        magnifText.grid(column=1,row=11, sticky="EW")
        #S/N
        signoiseLabel = Tkinter.Label(self,text=u"Signal-to-Noise ratio")
        signoiseLabel.grid(column=0,row=12,sticky="EW")
        signoiseText = Tkinter.Entry(self, textvariable=self.signoiseVar)
        signoiseText.grid(column=1,row=12, sticky="EW")
        #Intensity
        intensityLabel = Tkinter.Label(self,text=u"Intensity")
        intensityLabel.grid(column=0,row=13,sticky="EW")
        intensityText = Tkinter.Entry(self, textvariable=self.intensityVar)
        intensityText.grid(column=1,row=13, sticky="EW")


        #Save settings and run simulation or cancel with buttons
        runButton = Tkinter.Button(self, text=u"Save & Run", command=self.runcomm)
        runButton.grid(column=2,row=12, sticky="EW")
        cancelButton = Tkinter.Button(self, text=u"Cancel", command=self.destroy)
        cancelButton.grid(column=2,row=13, sticky="EW")

        self.grid_columnconfigure(1,weight=1)
        

    def setDiffs(self):
        fra = Tkinter.Toplevel(self)
        fra.wm_title("Diffusion Constants")
        fra.grid()
        #D1
        diff1Label = Tkinter.Label(fra, text=u"Diff const 1 [um^2/s]")
        diff1Label.grid(column=0,row=1,sticky="EW")
        diff1Text = Tkinter.Entry(fra, textvariable=self.diff1Var)
        diff1Text.grid(column=1,row=1,sticky="EW")
        if int(self.numStates.get()) >=2:
            #D2
            diff2Label = Tkinter.Label(fra, text=u"Diff const 2 [um^2/s]")
            diff2Label.grid(column=0,row=2,sticky="EW")
            diff2Text = Tkinter.Entry(fra, textvariable=self.diff2Var)
            diff2Text.grid(column=1,row=2, sticky="EW")
            if int(self.numStates.get()) >=3:
                #D3
                diff3Label = Tkinter.Label(fra, text=u"Diff const 3 [um^2/s]")
                diff3Label.grid(column=0,row=3,sticky="EW")
                diff3Text = Tkinter.Entry(fra, textvariable=self.diff3Var)
                diff3Text.grid(column=1,row=3, sticky="EW")
            else:
                self.diff3Var.set("")
        else:
            self.diff2Var.set("")

        def saveDiffs():
            fra.destroy()
        
        closeButton = Tkinter.Button(fra, text=u"Close", command=saveDiffs)
        closeButton.grid(column=1,row=4)

        fra.mainloop()
        

    def runcomm(self):
        if self.checkVars():
            self.destroy()
        else:
            return


if __name__ == "__main__":
    root = Tkinter.Tk(None)
    app = Simulation_App(root)
    app.pack()
    root.mainloop()
