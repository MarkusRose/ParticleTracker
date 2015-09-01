import Tkinter
import ttk
import tkFileDialog
import tkMessageBox
import sys

import os

import Detection.det_and_track as Detection

class guiDetection(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self,parent)
        self.parent = parent
        self.doSetup()

    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)
        ttk.Button(self, text="Set", command=self.updateVars).grid(column=1,row=2, sticky='S')
        ttk.Button(self, text="Reset", command=self.reload).grid(column=1,row=3)

        ttk.Button(self, text="Run", command=self.runDetection).grid(column=2,row=2, sticky="SE")
        ttk.Button(self, text="Cancel", command=self.destroy).grid(column=2,row=3, sticky='E')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)

        self.invar1 = Tkinter.StringVar()
        self.outvar1 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Input Images").grid(column=1, row=1, sticky='W')
        ttk.Button(self.labelframe, text="Choose", command = lambda:self.chooseDirectory(self.invar1)).grid(column=2, row=1, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar1).grid(column=3, row=1, sticky='W')

        self.invar2 = Tkinter.StringVar()
        self.outvar2 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Sigma").grid(column=1, row=2, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar2).grid(column=2, row=2, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar2).grid(column=3, row=2, sticky='W')

        self.invar3 = Tkinter.StringVar()
        self.outvar3 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Signal Power").grid(column=1, row=3, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar3).grid(column=2, row=3, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar3).grid(column=3, row=3, sticky='W')

        self.invar4 = Tkinter.StringVar()
        self.outvar4 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Image Bit Depth").grid(column=1, row=4, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar4).grid(column=2, row=4, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar4).grid(column=3, row=4, sticky='W')

        self.invar5 = Tkinter.StringVar()
        self.outvar5 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Maximum displacement").grid(column=1, row=5, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar5).grid(column=2, row=5, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar5).grid(column=3, row=5, sticky='W')

        self.invar6 = Tkinter.StringVar()
        self.outvar6 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Number of Images to add up").grid(column=1, row=6, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar6).grid(column=2, row=6, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar6).grid(column=3, row=6, sticky='W')

        self.invar7 = Tkinter.StringVar()
        self.outvar7 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Sigma Threshold").grid(column=1, row=7, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar7).grid(column=2, row=7, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar7).grid(column=3, row=7, sticky='W')

        self.invar8 = Tkinter.StringVar()
        self.outvar8 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Eccentricity Threshold").grid(column=1, row=8, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar8).grid(column=2, row=8, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar8).grid(column=3, row=8, sticky='W')

        self.invar9 = Tkinter.StringVar()
        self.outvar9 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Local maximum window size").grid(column=1, row=9, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar9).grid(column=2, row=9, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar9).grid(column=3, row=9, sticky='W')

        self.invar10 = Tkinter.StringVar()
        self.outvar10 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Minimum track length").grid(column=1, row=10, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar10).grid(column=2, row=10, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar10).grid(column=3, row=10, sticky='W')

        self.invar11 = Tkinter.StringVar()
        self.outvar11 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Initial Positions File").grid(column=1, row=11, sticky='W')
        ttk.Button(self.labelframe, text="Choose", command = lambda:self.chooseFile(self.invar11)).grid(column=2, row=11, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.invar11).grid(column=3, row=11, sticky='W')

        self.invar12 = Tkinter.StringVar()
        self.outvar12 = Tkinter.StringVar()
        ttk.Label(self.labelframe, text="Output Folder").grid(column=1, row=12, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.invar12).grid(column=2, row=12, sticky='W')
        ttk.Label(self.labelframe, textvariable=self.outvar12).grid(column=3, row=12, sticky='W')

        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        self.reload()
    


    def reload(self):
        if os.path.isfile("setup.txt"):
            infile = open("setup.txt",'r')
            infile.readline()
            infile.readline()
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar1.set(a.strip())
            self.outvar1.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar2.set(a.strip())
            self.outvar2.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar3.set(a.strip())
            self.outvar3.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar4.set(a.strip())
            self.outvar4.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar5.set(a.strip())
            self.outvar5.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar6.set(a.strip())
            self.outvar6.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar7.set(a.strip())
            self.outvar7.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar8.set(a.strip())
            self.outvar8.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar9.set(a.strip())
            self.outvar9.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar10.set(a.strip())
            self.outvar10.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar11.set(a.strip())
            self.outvar11.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            self.invar12.set(a.strip())
            self.outvar12.set(a.strip())
            infile.close()
        else:
            self.printVars()
        return


    def printVars(self):
        outfile = open("setup.txt",'w')
        outfile.write("#This is the setup file for ParticleSearcher\n#The following values can be adjusted\n\n")
        outfile.write("#Folder with input images:\n")
        if self.outvar1.get()=="":
            self.outvar1.set("Please select Folder containing Images")
        outfile.write(self.outvar1.get()+'\n\n#Sigma:\n')
        if self.outvar2.get()=="":
            self.outvar2.set("2")
        outfile.write(self.outvar2.get()+'\n\n#Signal Power:\n')
        if self.outvar3.get()=="":
            self.outvar3.set("1")
        outfile.write(self.outvar3.get()+'\n\n#Image Bit Depth:\n')
        if self.outvar4.get()=="":
            self.outvar4.set("16")
        outfile.write(self.outvar4.get()+'\n\n#Maximum Displacement:\n')
        if self.outvar5.get()=="":
            self.outvar5.set("100")
        outfile.write(self.outvar5.get()+'\n\n#Number of Images to add:\n')
        if self.outvar6.get()=="":
            self.outvar6.set("1")
        outfile.write(self.outvar6.get()+'\n\n#Sigma Threshold:\n')
        if self.outvar7.get()=="":
            self.outvar7.set("1")
        outfile.write(self.outvar7.get()+'\n\n#Eccentricity Threshold:\n')
        if self.outvar8.get()=="":
            self.outvar8.set("1")
        outfile.write(self.outvar8.get()+'\n\n#Local_Max_Window:\n')
        if self.outvar9.get()=="":
            self.outvar9.set("10")
        outfile.write(self.outvar9.get()+'\n\n#Minimum track length:\n')
        if self.outvar10.get()=="":
            self.outvar10.set("1")
        outfile.write(self.outvar10.get()+'\n\n#Read Initial position from:\n')
        if self.outvar11.get()=="":
            self.outvar11.set("#")
        outfile.write(self.outvar11.get()+'\n\n#Read Output Directory\n')
        if self.outvar12.get()=="":
            self.outvar12.set("AnalyzedData")
        outfile.write(self.outvar12.get()+'\n')
        outfile.close()
        return
    
    def updateVars(self):
        self.outvar1.set(self.invar1.get())
        self.outvar2.set(self.invar2.get())
        self.outvar3.set(self.invar3.get())
        self.outvar4.set(self.invar4.get())
        self.outvar5.set(self.invar5.get())
        self.outvar6.set(self.invar6.get())
        self.outvar7.set(self.invar7.get())
        self.outvar8.set(self.invar8.get())
        self.outvar9.set(self.invar9.get())
        self.outvar10.set(self.invar10.get())
        self.outvar11.set(self.invar11.get())
        self.outvar12.set(self.invar12.get())
        return 


    def chooseDirectory(self,var):
        dirname = tkFileDialog.askdirectory()
        if len(dirname) > 0:
            var.set(dirname)
            self.outvar1.set(var.get())
        else:
            self.outvar1.set("Please Select input Folder containing Images.")
        return
    
    def chooseFile(self,var):
        filename = tkFileDialog.askopenfilename()
        if len(filename) > 0:
            var.set(filename)
        return

    def checkInputs(self):
        try:
            #Input Images Folder exists
            if not os.path.isdir(self.outvar1.get()):
                tkMessageBox.showerror("No Images", "Images could not be located.")
                return False
            
            #Sigma positiv float
            if float(self.outvar2.get()) <= 0:
                self.outvar2.set("2")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Signal power
            if float(self.outvar3.get()) < 1:
                self.outvar3.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Image Bit Depth
            if int(self.outvar4.get()) < 8:
                self.outvar4.set("16")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Maximum displacement
            if float(self.outvar5.get()) <=0 :
                self.outvar5.set("100")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Number of Images to add up
            if int(self.outvar6.get()) < 1:
                self.outvar6.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Sigma threshold
            if float(self.outvar7.get()) < 0:
                self.outvar7.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #eccentricity threshold
            if float(self.outvar8.get()) <= 0:
                self.outvar8.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Local maximum window size
            if int(self.outvar9.get()) < 1:
                self.outvar9.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #minimum track length
            if int(self.outvar10.get())<1:
                self.outvar10.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to defaults.")
                return False

            #Initial Positions File
            #Output Folder
            if os.path.isdir(self.invar12.get()):
                if not tkMessageBox.askyesno("Folder Exists!", "This folder exists. Do you want to copy over its content?"):
                    return False
        except ValueError:
            tkMessageBox.showerror("NaN", "One of the entries is not correct (not a number).")
            return False

        return True
            
            
    def runDetection(self):
        if self.checkInputs():
            #print "Works now"
            self.printVars()
            self.destroy
            detector = Detection.detectAndTrack()
            detector.runDetectionAndTracking()
        else:
            print "Wrong inputs"
        return



if __name__ == "__main__":
    root = Tkinter.Tk(None)
    root.title("Particle Tracker Setup")
    app = guiDetection(root)
    app.pack()
    root.mainloop()

