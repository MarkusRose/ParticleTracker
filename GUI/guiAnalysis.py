import Tkinter as tk
import ttk
import sys
import tkFileDialog
import tkMessageBox
import os
import Queue
import threading
import time



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
        options['initialdir'] = os.environ["HOME"]+'/Desktop/'
        options['parent'] = self
        options['title'] = 'Select Track File'

        def fileSelect():
            self.v_trackFile.set( tkFileDialog.askopenfilename(**self.file_opt))
            return

        #----------------------------
        self.f_individTrack = tk.IntVar()
        tk.Checkbutton(self, text="MSD and step-size distribution - Multiple Tracks", variable=self.f_individTrack).pack(anchor='w')
        frame_iT = tk.Frame(self)
        tk.Label(frame_iT, text="Label1").grid(row=0)
        tk.Label(frame_iT, text="Label2").grid(row=1,column=1)
        frame_iT.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        self.f_combTrack = tk.IntVar()
        tk.Checkbutton(self, text="MSD and step-size distribution - Combined Track", variable=self.f_combTrack).pack(anchor='w')
        frame_CT = tk.Frame(self)
        tk.Label(frame_CT, text="").grid(sticky='e')
        tk.Label(frame_CT, text="").grid(sticky='e')
        frame_CT.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
        self.f_mcmc = tk.IntVar()
        tk.Checkbutton(self, text="Markov Chain Monte Carlo", variable=self.f_mcmc).pack(anchor='w')
        frame_MCMC = tk.Frame(self)
        tk.Label(frame_MCMC, text="").grid(row=0,sticky='e')
        tk.Label(frame_MCMC, text="").grid(row=1,sticky='e')
        frame_MCMC.pack()
        ttk.Separator(self).pack(fill='x',expand=1)
        #----------------------------
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
        tk.Label(frame_GP, text=u"Pixel Size [um]").grid(row=0,sticky='w')
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

        tk.Button(self, text="Analyze", command=self.analyze).pack()
        tk.Button(self, text="Cancel", command=self.exitWindow).pack()
        return

    def exitWindow(self):
        self.grab_release()
        self.parent.destroy()
        return

    def analyze(self):
        q = Queue.Queue()
        def on_main_thread(func):
            q.put(func)
            return

        def check_queue():
            while True:
                try:
                    task = q.get(block=False)
                except Queue.Empty:
                    break
                else:
                    self.after_idle(task)
            self.after(100,check_queue)
            return

        def calc_indiv_track():
            def done_mssg():
                tkMessageBox.showinfo("Done!", "Individual Track Analysis finished without problems.")
            time.sleep(30)
            on_main_thread(top1.destroy)
            on_main_thread(done_mssg)
            return

        def calc_comb_track():
            def done_mssg():
                tkMessageBox.showinfo("Done!", "Combined Track Analysis finished without problems.")
            time.sleep(10)
            on_main_thread(top2.destroy)
            on_main_thread(done_mssg)
            return

        def calc_mcmc():
            def done_mssg():
                tkMessageBox.showinfo("Done!", "MCMC finished without problems.")
            time.sleep(1)
            on_main_thread(top3.destroy)
            on_main_thread(done_mssg)
            return

        def calc_sci():
            def done_mssg():
                tkMessageBox.showinfo("Done!", "SCI finished without problems.",parent=self.parent)
            time.sleep(20)
            on_main_thread(top4.destroy)
            on_main_thread(done_mssg)
            return

        if int(self.f_individTrack.get()) == 1:
            print("individual tracks")
            top1 = tk.Toplevel(self)
            top1.title("Individual Track")
            top1.geometry("150x150+50+50")
            tk.Message(top1, text="Analyzing all individual tracks. This might take a while.", padx=20, pady=20).pack()
            t1 = threading.Thread(target=calc_indiv_track)
            t1.start()
        if int(self.f_combTrack.get()) == 1:
            print("Combined Track")
            top2 = tk.Toplevel(self)
            top2.title("Combined Track")
            top2.geometry("150x150+200+50")
            tk.Message(top2, text="Combining Tracks and analyzing all. This might take a while.", padx=20, pady=20).pack()
            t2 = threading.Thread(target=calc_comb_track)
            t2.start()
        if int(self.f_mcmc.get()) == 1:
            print("Monte Carlo")
            top3 = tk.Toplevel(self)
            top3.title("Markov Chain Monte Carlo")
            top3.geometry("150x150+350+50")
            tk.Message(top3, text="Doing a Markov Chain Monte Carlo analysis. This might take a while.", padx=20, pady=20).pack()
            t3 = threading.Thread(target=calc_mcmc)
            t3.start()
        if int(self.f_sci.get()) == 1:
            print("Speed Correlation Index")
            top4 = tk.Toplevel(self)
            top4.title("Speed Correlation Index")
            top4.geometry("150x150+500+50")
            tk.Message(top4, text="Doing a speed correlation index analysis. This will take a while.", padx=20, pady=20).pack()
            t4 = threading.Thread(target=calc_sci)
            t4.start()
        self.after(100,check_queue)
        sys.stdout.flush()
        return

