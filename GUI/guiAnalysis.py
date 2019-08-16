
import sys
import os
import os.path
import threading
import time
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
except ImportError:
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox

try:
    import Queue as queue
except ImportError:
    import queue
    

import AnalysisTools.ana_singlestate_legacy as ANA
#import AnalysisTools.ana_singlestate as ANA
import AnalysisTools.hiddenMarkov as HMM
import AnalysisTools.speedCorrelationIndex as SCI



class guiAnalysis(tk.Frame):
    def __init__(self,parent=None):
        tk.Frame.__init__(self,parent)
        self.parent= parent
        self.doSetup()
        self.grab_set()
        return

    def doSetup(self):

        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt'),('all files', '.*')]
        options['initialdir'] = './' #os.path.expanduser("~")+'/Desktop/'
        options['parent'] = self
        options['title'] = 'Select Track File'

        def fileSelect():
            self.v_trackFile.set( filedialog.askopenfilename(**self.file_opt))
            return

        #----------------------------
        #individual tracks gui
        self.f_individTrack = tk.IntVar()
        tk.Checkbutton(self, text="MSD and step-size distribution - Multiple Tracks", variable=self.f_individTrack).pack(anchor='w')
        frame_iT = tk.Frame(self)
        tk.Label(frame_iT, text="").grid(row=1,column=0)
        frame_iT.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        #combined tracks gui
        self.f_combTrack = tk.IntVar()
        tk.Checkbutton(self, text="MSD and step-size distribution - Combined Track", variable=self.f_combTrack).pack(anchor='w')
        frame_CT = tk.Frame(self)
        tk.Label(frame_CT, text="Minimum Track Length").grid(row=0,sticky='w')
        self.v_minTrLength = tk.StringVar()
        self.v_minTrLength.set("10")
        tk.Entry(frame_CT, textvariable=self.v_minTrLength).grid(row=0,column=1,sticky='ew')
        tk.Label(frame_CT, text="Fitrange in multiples of average Track length").grid(row=1,sticky='w')
        self.v_fitrange = tk.StringVar()
        self.v_fitrange.set("0.5")
        tk.Entry(frame_CT, textvariable=self.v_fitrange).grid(row=1,column=1,sticky='ew')
        tk.Label(frame_CT, text="").grid(sticky='e')
        frame_CT.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        #MCMC gui
        self.f_mcmc = tk.IntVar()
        tk.Checkbutton(self, text="Markov Chain Monte Carlo", variable=self.f_mcmc).pack(anchor='w')
        frame_MCMC = tk.Frame(self)
        tk.Label(frame_MCMC, text="Monte Carlo Runs").grid(row=0,sticky='e')
        self.v_montecarlo = tk.StringVar()
        self.v_montecarlo.set('10000')
        tk.Entry(frame_MCMC,textvariable=self.v_montecarlo).grid(row=0,column=1,sticky='e')
        frame_MCMC.pack()
        tk.Label(frame_MCMC, text="Identifier").grid(row=1,sticky='e')
        self.v_mcmcID = tk.StringVar()
        self.v_mcmcID.set('')
        tk.Entry(frame_MCMC,textvariable=self.v_mcmcID).grid(row=1,column=1,sticky='e')
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        #SCI gui
        self.f_sci = tk.IntVar()
        tk.Checkbutton(self, text="Speed-Correlation Index",variable=self.f_sci).pack(anchor='w')
        frame_SCI = tk.Frame(self)
        tk.Label(frame_SCI, text="").grid(sticky='e')
        tk.Label(frame_SCI, text="").grid(sticky='e')
        frame_SCI.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        tk.Label(self, text="General properties").pack(anchor='w')
        frame_GP = tk.Frame(self)
        tk.Label(frame_GP, text="Pixel Size [um]").grid(row=0,sticky='w')
        self.v_pixelSize = tk.StringVar()
        self.v_pixelSize.set("0.1")
        tk.Entry(frame_GP, textvariable=self.v_pixelSize).grid(row=0,column=1,sticky='ew')
        self.v_frameTime = tk.StringVar()
        self.v_frameTime.set("0.1")
        tk.Label(frame_GP, text="frame time [s]").grid(row=1,sticky='w')
        tk.Entry(frame_GP, textvariable=self.v_frameTime).grid(row=1,column=1,sticky='ew')
        self.v_trackFile = tk.StringVar()
        self.v_trackFile.set("Select File ...")
        tk.Button(frame_GP, text="Track File",command=fileSelect).grid(row=2,sticky='w')
        tk.Entry(frame_GP, textvariable=self.v_trackFile).grid(row=2,column=1,sticky='ew')
        frame_GP.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------

        self.anaButton = ttk.Button(self, text="Analyze", command=self.analyze)
        self.anaButton.pack()
        self.cancelButton = ttk.Button(self, text="Cancel", command=self.exitWindow)
        self.cancelButton.pack()
        return

    def exitWindow(self):
        self.grab_release()
        self.parent.destroy()
        return

    def checkInput(self):
        try:
            if not os.path.isfile(self.v_trackFile.get()):
                print("Invalid Filename")
                print((self.v_trackFile.get()))
                return False
            if float(self.v_pixelSize.get()) <= 0:
                print("Invalid Pixelsize")
                return False
            if float(self.v_frameTime.get()) <= 0:
                print("Invalid Frametime")
                return False
            if int(self.v_montecarlo.get()) <= 0:
                print("Invalid number of Monte Carlo runs")
                return False
            if int(self.v_minTrLength.get()) <= 0 :
                print("MinimumTrLength must be larger than 0.")
            if float(self.v_fitrange.get()) < 0:
                print("The fitrange must be positive.")
            #if self.v_mcmcID.get() <= 0:
            #    print("Invalid search radius for MCMC")
            #    return False
        except ValueError:
            print("ValueError")
            return False
        except TypeError:
            print("TypeError")
            return False
        return True

    def analyze(self):
        if self.checkInput():
            trackfile = self.v_trackFile.get()
            pxsize = float(self.v_pixelSize.get())
            frameT = float(self.v_frameTime.get())
            fitrange = float(self.v_fitrange.get())
            minTrLength= int(self.v_minTrLength.get())
            mcmcruns = int(self.v_montecarlo.get())
            mcmcID = self.v_mcmcID.get()
            q = queue.Queue()
            self.states = [True,True,True,True]
            def on_main_thread(func):
                q.put(func)
                return

            def check_queue():
                while True:
                    try:
                        task = q.get(block=False)
                    except queue.Empty:
                        break
                    else:
                        self.after_idle(task)
                if self.states[0] and self.states[1] and self.states[2] and self.states[3]:
                    enableButton()
                    return
                self.after(100,check_queue)
                return

            def calc_tracks_all():
                def done_mssg():
                    messagebox.showinfo("Done!", "All single-state Track Analysis finished without problems.")
                    return
                ANA.doAnalysis(trackfile,pixelsize=pxsize,frametime=frameT,minTrLength=minTrLength,fitrange=fitrange,bSingleTrackEndToEnd=True,bSingleTrackMSDanalysis=True,bCombineTrack=True)
                on_main_thread(top1.destroy)
                on_main_thread(done_mssg)
                self.states[0] = True
                self.states[1] = True
                return

            def calc_indiv_track():
                def done_mssg():
                    messagebox.showinfo("Done!", "Individual Track Analysis finished without problems.")
                ANA.doAnalysis(trackfile,pixelsize=pxsize,frametime=frameT,minTrLength=minTrLength,fitrange=fitrange,bCleanUpTracks=True,bSingleTrackEndToEnd=True,bSingleTrackMSDanalysis=True,bCombineTrack=False)
                on_main_thread(top1.destroy)
                on_main_thread(done_mssg)
                self.states[0] = True
                return

            def calc_comb_track():
                def done_mssg():
                    messagebox.showinfo("Done!", "Combined Track Analysis finished without problems.")
                ANA.doAnalysis(trackfile,pixelsize=pxsize,frametime=frameT,minTrLength=minTrLength,fitrange=fitrange,bSingleTrackEndToEnd=False,bSingleTrackMSDanalysis=False,bCombineTrack=True)
                on_main_thread(top1.destroy)
                on_main_thread(done_mssg)
                self.states[1] = True
                return

            def calc_mcmc():
                def done_mssg():
                    messagebox.showinfo("Done!", "MCMC finished without problems.")
                HMM.doHMM(trackfile,montecarlo=mcmcruns,SR=3)
                on_main_thread(top3.destroy)
                on_main_thread(done_mssg)
                self.states[2] = True
                return

            def calc_sci():
                def done_mssg():
                    messagebox.showinfo("Done!", "SCI finished without problems.",parent=self.parent)
                SCI.doSCI(trackfile)
                on_main_thread(top4.destroy)
                on_main_thread(done_mssg)
                self.states[3] = True
                return

            def disableButton():
                self.anaButton.state(['disabled'])
                self.cancelButton.state(['disabled'])
                return
            def enableButton():
                self.anaButton.state(['!disabled'])
                self.cancelButton.state(['!disabled'])
                return


            disableButton()
            if int(self.f_individTrack.get())+int(self.f_combTrack.get()) == 2:
                self.states[0] = False
                self.states[1] = False
                print("combined and individual")
                sys.stdout.flush()
                top1 = tk.Toplevel(self)
                top1.title("All Track Analysis")
                top1.geometry("150x150+50+50")
                tk.Message(top1, text="Doing all single-state track analysis. This might take a while.", padx=20, pady=20).pack()
                #t1 = threading.Thread(target=calc_tracks_all)
                #t1.start()
                self.after(100,calc_tracks_all)
            elif int(self.f_individTrack.get()) == 1:
                self.states[0] = False
                print("individual tracks")
                sys.stdout.flush()
                top1 = tk.Toplevel(self)
                top1.title("Individual Track")
                top1.geometry("150x150+50+50")
                tk.Message(top1, text="Analyzing all individual tracks. This might take a while.", padx=20, pady=20).pack()
                #t1 = threading.Thread(target=calc_indiv_track)
                #t1.start()
                self.after(100,calc_indiv_track)
            elif int(self.f_combTrack.get()) == 1:
                self.states[1] = False
                print("Combined Track")
                sys.stdout.flush()
                top1 = tk.Toplevel(self)
                top1.title("Combined Track")
                top1.geometry("150x150+200+50")
                tk.Message(top1, text="Combining Tracks and analyzing all. This might take a while.", padx=20, pady=20).pack()
                #t1 = threading.Thread(target=calc_comb_track)
                #t1.start()
                self.after(100,calc_comb_track)

            if int(self.f_mcmc.get()) == 1:
                self.states[2] = False
                print("Monte Carlo")
                top3 = tk.Toplevel(self)
                top3.title("Markov Chain Monte Carlo")
                top3.geometry("150x150+350+50")
                tk.Message(top3, text="Doing a Markov Chain Monte Carlo analysis. This might take a while.", padx=20, pady=20).pack()
                t3 = threading.Thread(target=calc_mcmc)
                t3.start()
            if int(self.f_sci.get()) == 1:
                self.states[3] = False
                print("Speed Correlation Index")
                top4 = tk.Toplevel(self)
                top4.title("Speed Correlation Index")
                top4.geometry("150x150+500+50")
                tk.Message(top4, text="Doing a speed correlation index analysis. This will take a while.", padx=20, pady=20).pack()
                #t4 = threading.Thread(target=calc_sci)
                #t4.start()
                self.after(100,calc_sci)
            self.after(100,check_queue)
        else:
            messagebox.showerror("Input Error!","Some inputs are invalid!")
        return

