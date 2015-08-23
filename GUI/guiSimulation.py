import Tkinter
import tkMessageBox
import System.Fileio
import Simulation.enzymeDiffuser

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
        self.diff2Var.set("n/a")
        self.diff3Var.set("n/a")
        self.prob12 = Tkinter.StringVar()
        self.prob21 = Tkinter.StringVar()
        self.prob13 = Tkinter.StringVar()
        self.prob31 = Tkinter.StringVar()
        self.prob23 = Tkinter.StringVar()
        self.prob32 = Tkinter.StringVar()
        self.prob12.set("0.0")
        self.prob21.set("1.0")
        self.prob13.set("0.0")
        self.prob23.set("0.0")
        self.prob31.set("1.0")
        self.prob32.set("0.0")
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
            if int(self.numStates.get()) >=3:
                if (self.diff3Var.get() == "n/a" or float(self.diff3Var.get()) < 0):
                    tkMessageBox.showerror("D3 false", "Third Diffusion coefficient does not match!")
                    return False
                if ((self.prob13.get() == "0.0" or float(self.prob13.get()) <=0 or float(self.prob13.get()) >=1) or
                    (self.prob23.get() == "0.0" or float(self.prob23.get()) <=0 or float(self.prob23.get()) >=1) or
                    (self.prob31.get() == "0.0" or float(self.prob31.get()) <=0 or float(self.prob31.get()) >=1) or
                    (self.prob32.get() == "0.0" or float(self.prob32.get()) <=0 or float(self.prob32.get()) >=1)):
                    tkMessageBox.showerror("Probs false", "Transition probatilities concerning the third diffusion coefficient do not match number of states!")
                    return False
            if int(self.numStates.get()) >=2:
                if (self.diff2Var.get() == "n/a" or float(self.diff2Var.get()) < 0):
                    tkMessageBox.showerror("D2 false", "Second Diffusion coefficient does not match!")
                    return False
                if ((self.prob12.get() == "0.0" or float(self.prob12.get()) <=0 or float(self.prob12.get()) >=1) or
                    (self.prob21.get() == "0.0" or float(self.prob21.get()) <=0 or float(self.prob21.get()) >=1)):
                    tkMessageBox.showerror("Probs false", "Transition probatilities concerning the first and second diffusion coefficient do not match number of states!")
                    return False
            if (len(self.diff1Var.get()) == 0 or float(self.diff1Var.get()) < 0):
                tkMessageBox.showerror("D1 false", "First Diffusion coefficient does not match!")
                return False
            if int(self.numStates.get()) == 2:
                self.diff3Var.set("n/a")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("0.0")
                self.prob32.set("0.0")
            
            if int(self.numStates.get()) == 1:
                self.diff2Var.set("n/a")
                self.diff3Var.set("n/a")
                self.prob12.set("0.0")
                self.prob21.set("1.0")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("1.0")
                self.prob32.set("0.0")
            
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
        diffFrame = Tkinter.Frame(self)
        numDiffButton = Tkinter.Button(diffFrame, text=u"Set Diff.Const.", command=self.setDiffs)
        numDiffButton.grid(column=0,row=0, sticky="EW")
        l1 = Tkinter.Label(diffFrame,text="D1 = ")
        l1.grid(column = 1, row = 0)
        d1 = Tkinter.Label(diffFrame,textvariable=self.diff1Var)
        d1.grid(column = 2, row = 0)
        l1l = Tkinter.Label(diffFrame,text=" um^2/s")
        l1l.grid(column = 3, row = 0, sticky = "E")
        l2 = Tkinter.Label(diffFrame,text="D2 = ")
        l2.grid(column = 1, row = 1)
        d2 = Tkinter.Label(diffFrame,textvariable=self.diff2Var)
        d2.grid(column = 2, row = 1)
        l2l = Tkinter.Label(diffFrame,text=" um^2/s")
        l2l.grid(column = 3, row = 1, sticky = "E")
        l3 = Tkinter.Label(diffFrame,text="D3 = ")
        l3.grid(column = 1, row = 2)
        d3 = Tkinter.Label(diffFrame,textvariable=self.diff3Var)
        d3.grid(column = 2, row = 2)
        l3l = Tkinter.Label(diffFrame,text=" um^2/s")
        l3l.grid(column = 3, row = 2, sticky ="E")

        d12l = Tkinter.Label(diffFrame,text="p12 = ")
        d12l.grid(column=4, row=0)
        d21l = Tkinter.Label(diffFrame,text="p21 = ")
        d21l.grid(column=4, row=1)
        d13l = Tkinter.Label(diffFrame,text="p13 = ")
        d13l.grid(column=4, row=2)
        d23l = Tkinter.Label(diffFrame,text="p23 = ")
        d23l.grid(column=6, row=0)
        d31l = Tkinter.Label(diffFrame,text="p31 = ")
        d31l.grid(column=6, row=1)
        d32l = Tkinter.Label(diffFrame,text="p32 = ")
        d32l.grid(column=6, row=2)
        d12 = Tkinter.Label(diffFrame, textvariable=self.prob12)
        d12.grid(column=5, row=0)
        d21 = Tkinter.Label(diffFrame, textvariable=self.prob21)
        d21.grid(column=5, row=1)
        d13 = Tkinter.Label(diffFrame, textvariable=self.prob13)
        d13.grid(column=5, row=2)
        d23 = Tkinter.Label(diffFrame, textvariable=self.prob23)
        d23.grid(column=7, row=0)
        d31 = Tkinter.Label(diffFrame, textvariable=self.prob31)
        d31.grid(column=7, row=1)
        d32 = Tkinter.Label(diffFrame, textvariable=self.prob32)
        d32.grid(column=7, row=2)
        diffFrame.grid(column=0,row=1,rowspan=1, columnspan=3, sticky="EW")
        diffFrame.grid_columnconfigure(2,weight=1)
        diffFrame.grid_columnconfigure(5,weight=1)
        diffFrame.grid_columnconfigure(7,weight=1)

        
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
            prob12Label = Tkinter.Label(fra, text=u"p1->2 = ")
            prob12Label.grid(column=2,row=1,sticky="EW")
            prob21Label = Tkinter.Label(fra, text=u"p2->1 = ")
            prob21Label.grid(column=2,row=2,sticky="EW")
            prob12Text = Tkinter.Entry(fra, textvariable=self.prob12)
            prob12Text.grid(column=3,row=1,sticky="EW")
            prob21Label = Tkinter.Label(fra, text=u"p2->1 = ")
            prob21Label.grid(column=2,row=2,sticky="EW")
            prob21Text = Tkinter.Entry(fra, textvariable=self.prob21)
            prob21Text.grid(column=3,row=2,sticky="EW")
            if int(self.numStates.get()) >=3:
                #D3
                diff3Label = Tkinter.Label(fra, text=u"Diff const 3 [um^2/s]")
                diff3Label.grid(column=0,row=3,sticky="EW")
                diff3Text = Tkinter.Entry(fra, textvariable=self.diff3Var)
                diff3Text.grid(column=1,row=3, sticky="EW")
                prob13Label = Tkinter.Label(fra, text=u"p1->3 = ")
                prob13Label.grid(column=2,row=3,sticky="EW")
                prob13Text = Tkinter.Entry(fra, textvariable=self.prob13)
                prob13Text.grid(column=3,row=3,sticky="EW")
                prob23Label = Tkinter.Label(fra, text=u"p2->3 = ")
                prob23Label.grid(column=2,row=4,sticky="EW")
                prob23Text = Tkinter.Entry(fra, textvariable=self.prob23)
                prob23Text.grid(column=3,row=4,sticky="EW")
                prob31Label = Tkinter.Label(fra, text=u"p3->1 = ")
                prob31Label.grid(column=2,row=5,sticky="EW")
                prob31Text = Tkinter.Entry(fra, textvariable=self.prob31)
                prob31Text.grid(column=3,row=5,sticky="EW")
                prob32Label = Tkinter.Label(fra, text=u"p3->2 = ")
                prob32Label.grid(column=2,row=6,sticky="EW")
                prob32Text = Tkinter.Entry(fra, textvariable=self.prob32)
                prob32Text.grid(column=3,row=6,sticky="EW")
            else:
                self.diff3Var.set("n/a")
                self.prob13.set("0.0")
                self.prob23.set("0.0")
                self.prob31.set("0.0")
                self.prob32.set("0.0")
        else:
            self.diff2Var.set("n/a")
            self.prob12.set("0.0")
            self.prob21.set("1.0")
            self.prob13.set("0.0")
            self.prob23.set("0.0")
            self.prob31.set("1.0")
            self.prob32.set("0.0")

        def saveDiffs():
            fra.destroy()
        
        closeButton = Tkinter.Button(fra, text=u"Close", command=saveDiffs)
        closeButton.grid(column=1,row=7)

        fra.mainloop()

    def giveToProgram(self):
        outvar = []
        outvar.append(int(self.numStates.get()))
        outvar.append(float(self.diff1Var.get()))
        outvar.append(str(self.diff2Var.get()))
        outvar.append(str(self.diff3Var.get())) 
        outvar.append(str(self.prob12.get())) 
        outvar.append(str(self.prob21.get())) 
        outvar.append(str(self.prob13.get())) 
        outvar.append(str(self.prob23.get())) 
        outvar.append(str(self.prob31.get())) 
        outvar.append(str(self.prob32.get())) 
        outvar.append(str(self.numframesVar.get())) 
        outvar.append(str(self.numPartVar.get())) 
        outvar.append(str(self.tauVar.get())) 
        outvar.append(str(self.frameLengthVar.get())) 
        outvar.append(str(self.lambdaVar.get())) 
        outvar.append(str(self.pixsizeVar.get())) 
        outvar.append(str(self.naVar.get())) 
        outvar.append(str(self.magnifVar.get())) 
        outvar.append(str(self.signoiseVar.get())) 
        outvar.append(str(self.intensityVar.get())) 
        return outvar

        
    def runcomm(self):
        if self.checkVars():
            print "Everythings fine, running program now. Have to pass variables to Fileio.setSysProps with all the parameters given."
            System.Fileio.setSysProps(self.giveToProgram())
            self.destroy()
            Simulation.enzymeDiffuser.simulateTracks()
            print "Done"
        return


if __name__ == "__main__":
    root = Tkinter.Tk(None)
    app = Simulation_App(root)
    app.pack()
    root.mainloop()