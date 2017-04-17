import Tkinter
import ttk
import tkFileDialog
import tkMessageBox
import sys
import os
import time
import threading
import Queue

import Detection.det_and_track as Detection
import tracking

class guiTracking(Tkinter.Frame):
    def __init__(self,parent):
        Tkinter.Frame.__init__(self,parent)
        self.parent = parent
        self.doSetup()

    def doSetup(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(column=1, row=1)

        ttk.Button(self, text="Run", command=self.runTracking).grid(column=2,row=2, sticky="SE")
        ttk.Button(self, text="Cancel", command=self.parent.destroy).grid(column=2,row=3, sticky='E')
        
        self.labelframe = ttk.Frame(self.mainframe)
        self.labelframe.grid(column=0, row=0)

        self.inPosVar = Tkinter.StringVar()
        self.inPosVar.set("Please select position file.")
        ttk.Button(self.labelframe, text="Positions File", command = lambda:self.inPosVar.set(tkFileDialog.askopenfilename())).grid(column=1, row=1, sticky='W')
        ttk.Label(self.labelframe,textvariable=self.inPosVar).grid(column=3, row=1, sticky='W')

        
        self.maxDispVar = Tkinter.StringVar()
        self.maxDispVar.set("3")
        ttk.Label(self.labelframe, text="Maximum displacement").grid(column=1, row=2, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.maxDispVar).grid(column=2, row=2, sticky='W')


        self.minTrVar = Tkinter.StringVar()
        self.minTrVar.set('1')
        ttk.Label(self.labelframe, text="Minimum track length").grid(column=1, row=3, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.minTrVar).grid(column=2, row=3, sticky='W')

        self.linkRaVar = Tkinter.StringVar()
        self.linkRaVar.set("2")
        ttk.Label(self.labelframe, text="Link range (frameskip)").grid(column=1, row=4, sticky='W')
        ttk.Entry(self.labelframe, textvariable = self.linkRaVar).grid(column=2, row=4, sticky='W')


        for child in self.labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)

        return    


    def checkInputs(self):
        try:
            if not os.path.isfile(self.inPosVar.get()):
                tkMessageBox.showerror("Not a file", "File does not exist. Please choose the correct file!")
                return False
            #Maximum displacement
            if float(self.maxDispVar.get()) <=0 :
                self.maxDispVar.set("2")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to 2px.")
                return False

            #minimum track length
            if int(self.minTrVar.get())<1:
                self.minTrVar.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Reset to track length of 1.")
                return False

            #link range
            if int(self.linkRaVar.get())<1:
                self.minTrVar.set("1")
                tkMessageBox.showwarning("Reset Value", "Value(s) was/were incorrect. Link range set to 1.")
                return False

            #Initial Positions File
            #Output Folder
            if os.path.isdir(os.path.dirname(self.inPosVar.get())):
                if not tkMessageBox.askyesno("Folder Exists!", "This folder exists. Some content might be lost. Continue?"):
                    return False
        except ValueError:
            tkMessageBox.showerror("NaN", "One of the entries is not correct (not a number).")
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

            top = Tkinter.Toplevel()
            top.title("Tracking running")
            Tkinter.Message(top, text="Tracking now. This might take a while.", padx=20, pady=20).pack()
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
                tkMessageBox.showinfo("Done!", "Tracking finished without problems.")

            def add_task():
                return 0

            def handle_calc():
                def calculator():
                    time.sleep(4)
                    if not os.path.isdir(outv[4]):
                        os.mkdir(outv[4])
                    os.chdir(outv[4])
                    tracking.doTrack(outv[0],searchRadius=outv[1],minTracklen=outv[2],linkRange=outv[3])
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
    app = guiTracking(root)
    app.pack()
    root.mainloop()
