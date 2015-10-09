b Initial position from:\n')
        if self.outvar11.get()=="":
            self.outvar11.set("#")
        outfile.write(self.outvar11.get()+'\n\n#Read Output Directory\n')
        if self.outvar12.get()=="":
            self.outvar12.set("AnalyzedData")
        outfile.write(self.outvar12.get()+'\n\n#Detection Method\n')
        if self.outvar13.get()=="":
            self.outvar13.set("0")
        outfile.write(self.outvar13.get()+'\n')
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
        if self.invar13.get() == self.detMethod[0]:
            self.outvar13.set("0")
        else:
            self.outvar13.set("1")
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
            if float(self.outvar3.get()) <= 0:
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

            #Method of detection
            if self.invar13 == self.detMethod[0]:
                self.outvar13.set("0")
            else:
                self.outvar13.set("1")
        except ValueError:
            tkMessageBox.showerror("NaN", "One of the entries is not correct (not a number).")
            return False

        return True
            
            
    def runDetandTrack(self):
        self.updateVars()
        self.printVars()
        #print self.invar13.get()
        #print self.outvar13.get()
        if self.checkInputs():
            #print "Works now"
            self.destroy
            detector = Detection.detectAndTrack()
            detector.runDetectionAndTracking()
            #print self.invar13.get()
            #print self.outvar13.get()
        else:
            #print self.invar13.get()
            #print self.outvar13.get()
            print "Wrong inputs"
        return



if __name__ == "__main__":
    root = Tkinter.Tk(None)
    root.title("Particle Tracker Setup")
    app = guiDetection(root)
    app.pack()
    root.mainloop()

