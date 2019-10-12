import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import sys

#==========================================
'''Figure formatting options'''
#******************************************
from matplotlib import rcParams, colors
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import itertools

matplotlib.use('Agg')
#plt.style.use('ggplot')

iw = 6.69

rcParams['font.family']='sans-serif'
rcParams['font.size']=8
rcParams['lines.markersize']=1
rcParams['lines.linewidth']=1
rcParams['figure.dpi']=600
rcParams['text.usetex']=True
rcParams['text.latex.preamble']=[
        r'\usepackage{siunitx}',
        r'\usepackage{amsmath,amssymb}',
        r'\usepackage{sansmath}',
        r'\sansmath'
        ]
#******************************************
#==========================================

tau = 1

def fillMissingSteps(df_track):
    df_track_array = df_track[['#Step','x','y']].values[:]
    df_displace = df_track_array[1:] - df_track_array[:-1]
    index_saver = np.where(df_displace[:,0] != 1)[0]
    df_track_list = list(df_track_array)
    count = 0
    for i in index_saver:
        track_index = i + count
        for j in range(1,int(df_displace[i,0]),1):
            newtime = df_track_array[i,0]+j
            next_x = df_track_array[i,1] + df_displace[i,1]/df_displace[i,0] * j
            next_y = df_track_array[i,2] + df_displace[i,2]/df_displace[i,0] * j
            df_track_list.insert(track_index+j,np.array([newtime,next_x,next_y]))
            count += 1
    return np.array(df_track_list)


def makeRadialDistribution(filename,p0=[1e-4,1e-5,100,100],amplitudef=False):
    df_track = pd.read_csv(filename,sep=' ')
    df_track_array = fillMissingSteps(df_track)

    results = []
    colors = ['r','b','g','m']
    plottimelist = np.arange(len(colors))*4+1
    lagtimelist = np.arange(40)+1
    plt.figure(figsize=(iw/3,iw/3))
    count = 0
    for lag in lagtimelist:
        df_displace = df_track_array[lag:] - df_track_array[:-lag]
        df_displace = np.sqrt(df_displace[:,1]**2 + df_displace[:,2]**2) * 0.067
	
        def radialStep(x,D,A):
            tau = lag
            return A*x/(2*D*tau)*np.exp(-x**2/(4*D*tau))

        def twoRadialDiffusion(x,D1,D2,A1,A2):
            return radialStep(x,D1,A1) + radialStep(x,D2,A2)

        dr = np.histogram(df_displace,bins=500,range=(0,0.5))
        rvals = (dr[1][1:] + dr[1][:-1])/2
        binwidth = np.mean(dr[1][1:] - dr[1][:-1])

        popt,pcov = curve_fit(twoRadialDiffusion,rvals,dr[0],p0=p0)
        if popt[0] < popt[1]:
            dsav = popt[1]
            popt[1] = popt[0]
            popt[0] = dsav
            dsav = popt[2]/binwidth
            popt[2] = popt[3]/binwidth
            popt[3] = dsav

        if lag in plottimelist:
            plt.plot(rvals,dr[0],colors[count]+'o')
            plt.plot(rvals,twoRadialDiffusion(rvals,popt[0],popt[1],popt[2],popt[3]),label=r"{:}".format(lag)+" \si{s} lag",color=colors[count])
            count += 1
        results.append(popt)

    df = pd.DataFrame(results,columns=['D1','D2','N1','N2'])
    df['lagtime'] = lagtimelist
    plt.xlabel(r"$\Delta r^2 [\si{\mu m}^2]$")
    plt.ylabel(r"Counts")
    ax1 = plt.gca()
    ax1.ticklabel_format(axis='y',style='sci',scilimits=(3,3),useMathText=False)
    plt.tight_layout()
    plt.legend()
    plt.savefig(os.path.join(os.path.split(filename)[0],"combined-radialDisplacement.png"))
    plt.close()

    n1parts = df['N1']
    n2parts = df['N2']
    ntotal = n1parts + n2parts
    #ntotal = 1
    df['Daverage'] = (n1parts * df['D1'] + n2parts * df['D2'])/ntotal

    plt.figure(figsize=(iw/3,iw/3))
    ax1 = plt.gca()
    plt.plot(df['lagtime'],df['D1'],'ro',label='D1')
    plt.plot(df['lagtime'],df['D2'],'bo',label='D2')
    plt.plot(df['lagtime'],df['Daverage'],'y^',label=r"$\bar{D}$")
    plt.xlabel("Lag time $[\si{s}]$")
    plt.ylabel("Diffusion Coefficient $[\si{\mu m}^2\si{s}^{-1}]$")
    plt.gca().set_ylim(bottom=0)
    ax1.ticklabel_format(axis='y',style='sci',scilimits=(-4,-4),useMathText=False)
    plt.legend()
    ax2 = ax1.twinx()
    ax2.plot(df['lagtime'],n1parts/ntotal,'mx',label='N1')
    ax2.plot(df['lagtime'],n2parts/ntotal,'cx',label='N1')
    ax2.set_ylabel("NumDisplacements",color='r')
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"combined-radialDisplacement-lagdependence.png"))
    plt.close()

    radmean = df.iloc[0]
    df.to_csv(os.path.join(os.path.split(filename)[0],"TwoStateDiffusionAverages_radial.csv"))

    return pd.DataFrame(radmean[['D1','D2','A1','A2']]).transpose()



def makeDoubleGauss(filename,p0=[1e-4,1e-5,100,100],amplitudef=False):
    df_track = pd.read_csv(filename,sep=' ')
    df_track_array = fillMissingSteps(df_track)
    
    results = []
    lagtimelist = np.arange(40) + 1
    colors = ['r','b','g','m']
    plottimelist = np.arange(len(colors))*4+1
    plt.figure(figsize=(iw/3,iw/3))
    count = 0
    for lag in lagtimelist:
        df_displace = df_track_array[lag:] - df_track_array[:-lag]
        dx = np.histogram(df_displace[:,1:]*0.067,bins=500,range=(-0.5,0.5))
        xvals = (dx[1][1:]+dx[1][:-1])/2
        binwidth = np.mean(dx[1][1:]-dx[1][:-1])

        def gaussbell(x,D,A):
            tau = lag
            return A/np.sqrt(4*np.pi*D*tau) * np.exp(-(x)**2/(4*D*tau))

        def doubleGauss(x,D1,D2,A1,A2):
            return gaussbell(x,D1,A1) + gaussbell(x,D2,A2)

        popt,pcov = curve_fit(doubleGauss,xvals,dx[0],p0=p0)
        if popt[0] < popt[1]:
            dsav = popt[1]
            popt[1] = popt[0]
            popt[0] = dsav
            dsav = popt[2]/binwidth
            popt[2] = popt[3]/binwidth
            popt[3] = dsav

        if lag in plottimelist:
            plt.plot(xvals,dx[0],colors[count]+'o')
            plt.plot(xvals,doubleGauss(xvals,popt[0],popt[1],popt[2],popt[3]),color=colors[count],label=r"{:}".format(lag)+" \si{s} lag")
            count += 1
            #plt.plot(xvals,gaussbell(xvals,popt[0],popt[2]))
            #plt.plot(xvals,gaussbell(xvals,popt[1],popt[3]))
        results.append(popt)
    df = pd.DataFrame(results,columns=['D1','D2','N1','N2'])
    df['lagtime'] = lagtimelist
    plt.xlabel(r"$\Delta x [\si{\mu m}]$")
    plt.ylabel(r"Counts")
    ax1 = plt.gca()
    ax1.ticklabel_format(axis='y',style='sci',scilimits=(3,3),useMathText=False)
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"combined-diplacements.png"))
    plt.close()

    n1parts = df['N1']
    n2parts = df['N2']
    ntotal = n1parts + n2parts
    #ntotal = 1
    df['Daverage'] = (n1parts * df['D1'] + n2parts * df['D2'])/ntotal


    plt.figure(figsize=(iw/3,iw/3))
    ax1 = plt.gca()
    plt.plot(df['lagtime'],df['D1'],'ro',label='D1')
    plt.plot(df['lagtime'],df['D2'],'bo',label='D2')
    plt.xlabel(r"Lag time $[\si{s}]$")
    plt.ylabel(r"Diffusion Coefficient $[\si{\mu m}^2\si{s}^{-1}]$")
    plt.ylim(bottom=0)
    ax1.ticklabel_format(axis='y',style='sci',scilimits=(-4,-4),useMathText=False)
    ax2 = ax1.twinx()
    ax2.plot(df['lagtime'],n1parts/ntotal,'mx',label='N1')
    ax2.plot(df['lagtime'],n2parts/ntotal,'cx',label='N1')
    ax2.set_ylabel("NumDisplacements",color='r')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"combined-displacements-lagdependence.png"))
    plt.close()

    gaussmean = df.mean()
    gaussmean.to_csv(os.path.join(os.path.split(filename)[0],"TwoStateDiffusionAverages_gauss.csv"))

    return pd.DataFrame(gaussmean[['D1','D2','A1','A2']]).transpose()


def twoStateFit(tracklist,celtype,temp,SR,amplitudef):
    print("*"*72)
    print("Two State Fit")
    print("-"*30)
    count = 0
    #cols = ['CelType','Temperature','gaussD1','gaussD2','gaussA1','gaussA2','raddistD1','raddistD2','raddistA1','raddistA2']
    df = pd.DataFrame()
    for trackfile in tracklist:
        print(trackfile)
        try:
            dgauss = makeDoubleGauss(trackfile,p0=[1e-3,1e-4,100,100],amplitudef=amplitudef)

        except RuntimeError:
            dgauss = pd.DataFrame({'D1':[np.nan],'D2':[np.nan],'A1':[np.nan],'A2':[np.nan]})
        try:
            raddist = makeRadialDistribution(trackfile,p0=[1e-3,1e-4,100,100],amplitudef=amplitudef)
        except RuntimeError:
            raddist = pd.DataFrame({'D1':[np.nan],'D2':[np.nan],'A1':[np.nan],'A2':[np.nan]})
        middleman = pd.DataFrame({'CelType':[celtype[count]],'Temperature':[temp[count]]})
        dgauss.columns = ['gaussD1','gaussD2','gaussA1','gaussA2']
        raddist.columns = ['raddistD1','raddistD2','raddistA1','raddistA2']
        saverdf = pd.concat([middleman,dgauss,raddist],axis=1)
        df = pd.concat([df,saverdf],ignore_index=True,axis=0)

        count += 1

    print("*"*72)
    df.to_csv("TwoDiffusionSummary{:}.csv".format(SR))
    return


if __name__=="__main__":
    tracklist = []
    celtype = []
    temp = []
    SR = "_SR3.0"
    amplitudef = False
    for dirname,dirlist,filelist in os.walk('.'):
        if "SingleStateAnalysis{:}".format(SR) in dirname:
            if os.path.isfile(os.path.join(dirname,'combinedTrack.txt')):
                tracklist.append(os.path.join(dirname,'combinedTrack.txt'))
                dirarray = os.path.normpath(dirname).split(os.path.sep)
                celtype.append(dirarray[0][:5])
                temp.append(int(dirarray[1][:2]))
    twoStateFit(tracklist,celtype,temp,SR,amplitudef)

