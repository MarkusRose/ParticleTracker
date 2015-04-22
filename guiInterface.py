from Tkinter import *
import ttk

def runGUI():
    def doSetup():
        def exitSetup():
            labelframe.destroy()
            buttonframe.destroy()

        def finishSetup():
            updateText()
            labelframe.destroy()
            buttonframe.destroy()

        def reload():
            infile = open("setup.txt",'r')
            infile.readline()
            infile.readline()
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar1.set(a.strip())
            outvar1.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar2.set(a.strip())
            outvar2.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar3.set(a.strip())
            outvar3.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar4.set(a.strip())
            outvar4.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar5.set(a.strip())
            outvar5.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar6.set(a.strip())
            outvar6.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar7.set(a.strip())
            outvar7.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar8.set(a.strip())
            outvar8.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar9.set(a.strip())
            outvar9.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar10.set(a.strip())
            outvar10.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar12.set(a.strip())
            outvar12.set(a.strip())
            infile.readline()
            infile.readline()
            a = infile.readline()
            invar11.set(a.strip())
            outvar11.set(a.strip())
            infile.close()

        def updateText():
            outfile = open("setup.txt",'w')
            outfile.write("#This is the setup file for ParticleSearcher\n#The following values can be adjusted\n\n")
            outfile.write("#Folder with input images:\n")
            outvar1.set(invar1.get())
            if outvar1.get()=="":
                outvar1.set("#")
            outfile.write(outvar1.get()+'\n\n#Sigma:\n')
            outvar2.set(invar2.get())
            if outvar2.get()=="":
                outvar2.set("#")
            outfile.write(outvar2.get()+'\n\n#Signal Power:\n')
            outvar3.set(invar3.get())
            if outvar3.get()=="":
                outvar3.set("#")
            outfile.write(outvar3.get()+'\n\n#Image Bit Depth:\n')
            outvar4.set(invar4.get())
            if outvar4.get()=="":
                outvar4.set("#")
            outfile.write(outvar4.get()+'\n\n#Maximum Displacement:\n')
            outvar5.set(invar5.get())
            if outvar5.get()=="":
                outvar5.set("#")
            outfile.write(outvar5.get()+'\n\n#Number of Images to add:\n')
            outvar6.set(invar6.get())
            if outvar6.get()=="":
                outvar6.set("#")
            outfile.write(outvar6.get()+'\n\n#Sigma Threshold:\n')
            outvar7.set(invar7.get())
            if outvar7.get()=="":
                outvar7.set("#")
            outfile.write(outvar7.get()+'\n\n#Eccentricity Threshold:\n')
            outvar8.set(invar8.get())
            if outvar8.get()=="":
                outvar8.set("#")
            outfile.write(outvar8.get()+'\n\n#Local_Max_Window:\n')
            outvar9.set(invar9.get())
            if outvar9.get()=="":
                outvar9.set("#")
            outfile.write(outvar9.get()+'\n\n#Minimum track length:\n')
            outvar10.set(invar10.get())
            if outvar10.get()=="":
                outvar10.set("#")
            outfile.write(outvar10.get()+'\n\n#Read Output Directory\n')
            outvar12.set(invar12.get())
            if outvar12.get()=="":
                outvar12.set("#")
            outfile.write(outvar12.get()+'\n\n#Read Initial position from:\n')
            outvar11.set(invar11.get())
            if outvar11.get()=="":
                outvar11.set("#")
            outfile.write(outvar11.get()+'\n')
            outfile.close()

        mainframe = ttk.Frame(root)
        mainframe.grid(column=1, row=1)

        labelframe = ttk.Frame(mainframe)
        labelframe.grid(column=0, row=0)


        invar1 = StringVar()
        outvar1 = StringVar()
        ttk.Label(labelframe, text="Input Images").grid(column=1, row=1, sticky=W)
        ttk.Entry(labelframe, textvariable = invar1).grid(column=2, row=1, sticky=W)
        ttk.Label(labelframe, textvariable=outvar1).grid(column=3, row=1, sticky=W)

        invar2 = StringVar()
        outvar2 = StringVar()
        ttk.Label(labelframe, text="Sigma").grid(column=1, row=2, sticky=W)
        ttk.Entry(labelframe, textvariable = invar2).grid(column=2, row=2, sticky=W)
        ttk.Label(labelframe, textvariable=outvar2).grid(column=3, row=2, sticky=W)

        invar3 = StringVar()
        outvar3 = StringVar()
        ttk.Label(labelframe, text="Signal Power").grid(column=1, row=3, sticky=W)
        ttk.Entry(labelframe, textvariable = invar3).grid(column=2, row=3, sticky=W)
        ttk.Label(labelframe, textvariable=outvar3).grid(column=3, row=3, sticky=W)

        invar4 = StringVar()
        outvar4 = StringVar()
        ttk.Label(labelframe, text="Image Bit Depth").grid(column=1, row=4, sticky=W)
        ttk.Entry(labelframe, textvariable = invar4).grid(column=2, row=4, sticky=W)
        ttk.Label(labelframe, textvariable=outvar4).grid(column=3, row=4, sticky=W)

        invar5 = StringVar()
        outvar5 = StringVar()
        ttk.Label(labelframe, text="Maximum displacement").grid(column=1, row=5, sticky=W)
        ttk.Entry(labelframe, textvariable = invar5).grid(column=2, row=5, sticky=W)
        ttk.Label(labelframe, textvariable=outvar5).grid(column=3, row=5, sticky=W)

        invar6 = StringVar()
        outvar6 = StringVar()
        ttk.Label(labelframe, text="Number of Images to add up").grid(column=1, row=6, sticky=W)
        ttk.Entry(labelframe, textvariable = invar6).grid(column=2, row=6, sticky=W)
        ttk.Label(labelframe, textvariable=outvar6).grid(column=3, row=6, sticky=W)

        invar7 = StringVar()
        outvar7 = StringVar()
        ttk.Label(labelframe, text="Sigma Threshold").grid(column=1, row=7, sticky=W)
        ttk.Entry(labelframe, textvariable = invar7).grid(column=2, row=7, sticky=W)
        ttk.Label(labelframe, textvariable=outvar7).grid(column=3, row=7, sticky=W)

        invar8 = StringVar()
        outvar8 = StringVar()
        ttk.Label(labelframe, text="Eccentricity Threshold").grid(column=1, row=8, sticky=W)
        ttk.Entry(labelframe, textvariable = invar8).grid(column=2, row=8, sticky=W)
        ttk.Label(labelframe, textvariable=outvar8).grid(column=3, row=8, sticky=W)

        invar9 = StringVar()
        outvar9 = StringVar()
        ttk.Label(labelframe, text="Local maximum window size").grid(column=1, row=9, sticky=W)
        ttk.Entry(labelframe, textvariable = invar9).grid(column=2, row=9, sticky=W)
        ttk.Label(labelframe, textvariable=outvar9).grid(column=3, row=9, sticky=W)

        invar10 = StringVar()
        outvar10 = StringVar()
        ttk.Label(labelframe, text="Minimum track length").grid(column=1, row=10, sticky=W)
        ttk.Entry(labelframe, textvariable = invar10).grid(column=2, row=10, sticky=W)
        ttk.Label(labelframe, textvariable=outvar10).grid(column=3, row=10, sticky=W)

        invar12 = StringVar()
        outvar12 = StringVar()
        ttk.Label(labelframe, text="Output Folder").grid(column=1, row=11, sticky=W)
        ttk.Entry(labelframe, textvariable = invar12).grid(column=2, row=11, sticky=W)
        ttk.Label(labelframe, textvariable=outvar12).grid(column=3, row=11, sticky=W)

        invar11 = StringVar()
        outvar11 = StringVar()
        ttk.Label(labelframe, text="Initial Positions File").grid(column=1, row=12, sticky=W)
        ttk.Entry(labelframe, textvariable = invar11).grid(column=2, row=12, sticky=W)
        ttk.Label(labelframe, textvariable=outvar11).grid(column=3, row=12, sticky=W)


        for child in labelframe.winfo_children(): child.grid_configure(padx = 5, pady = 5)


        buttonframe = ttk.Frame(mainframe, width=root.winfo_width())
        buttonframe.grid(column = 0,row=1)
        ttk.Button(buttonframe, text="Set", command=updateText).grid(column=1,row=1, sticky=W)
        ttk.Button(buttonframe, text="Done", command=finishSetup).grid(column=2,row=1, sticky=W)
        ttk.Button(buttonframe, text="Cancel", command=exitSetup).grid(column=3,row=1, sticky=W)

        reload()

    root = Tk()
    root.title("Particle Tracker Setup")

    #doSetup()

    ttk.Button(root, text="Run", command=root.destroy).grid(column=0,row=2, sticky=W)
    ttk.Button(root, text="Setup", command=doSetup).grid(column=1,row=2, sticky=W)
    ttk.Button(root, text="Exit", command=sys.exit).grid(column=2,row=2, sticky=E)

    root.mainloop()

if __name__=="__main__":
    runGUI()

