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
#rcParams['errorbar.hattick']=1
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


def makeRadialDistribution(filename,amplitudef):
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
	
        def radialStep(x,D,N):
            tau = lag
            return N*x/(2*D*tau)*np.exp(-x**2/(4*D*tau))

        dr = np.histogram(df_displace,bins=500,range=(0,0.5))
        rvals = (dr[1][1:] + dr[1][:-1])/2
        binwidth = np.mean(dr[1][1:] - dr[1][:-1])

        popt,pcov = curve_fit(radialStep,rvals,dr[0],p0=[1e-4,300])
        SSres = np.sum((dr[0] - radialStep(rvals,popt[0],popt[1]))**2)
        SStot = np.sum((dr[0] - np.mean(dr[0]))**2)
        rsquared = 1 - SSres/SStot

        if lag in plottimelist:
            plt.plot(rvals,dr[0],colors[count]+'o',label="{:}".format(lag) + " s lag")
            plt.plot(rvals,radialStep(rvals,popt[0],popt[1]),label=r"{:}".format(lag)+" \si{s} lag",color=colors[count])
            count += 1
        results.append([popt[0],popt[1]/binwidth,rsquared])
    df = pd.DataFrame(results,columns=['D','N','Rsquared'])
    df['lagtime'] = lagtimelist
    plt.xlabel(r"$\Delta r^2 [\si{\mu m}^2]$")
    plt.ylabel(r"Count")
    ax1 = plt.gca()
    ax1.ticklabel_format(axis='y',style='sci',scilimits=(3,3),useMathText=False)
    plt.tight_layout()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"OneStateFit-radialDisplacement.png"))
    plt.close('all')

    df.to_csv(os.path.join(os.path.split(filename)[0],"OneStateDiffusionAverages_radial.csv"))

    radmean = df.iloc[0]#.mean()

    return pd.DataFrame(radmean[['D','N','Rsquared']]).transpose()


def makeGauss(filename,amplitudef):
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
        dx = np.histogram(df_displace[:,1:]*0.067,bins=500,range=(-0.5,0.5))
        xvals = (dx[1][1:]+dx[1][:-1])/2
        binwidth = np.mean(dx[1][1:] - dx[1][:-1])

        def gaussbell(x,D,A):
            tau = lag
            return A/np.sqrt(4*np.pi*D*tau) * np.exp(-(x)**2/(4*D*tau))

        popt,pcov = curve_fit(gaussbell,xvals,dx[0],p0=[1e-4,400])
        SSres = np.sum((dx[0] - gaussbell(xvals,popt[0],popt[1]))**2)
        SStot = np.sum((dx[0] - np.mean(dx[0]))**2)
        rsquared = 1 - SSres/SStot

        if lag in plottimelist:
            plt.plot(xvals,dx[0],colors[count]+"o",label ="{:}".format(lag) + " s lag, R$^2$"+" {:0.02f}".format(rsquared))
            plt.plot(xvals,gaussbell(xvals,popt[0],popt[1]),colors[count]+'-')
            count += 1
        results.append([popt[0],popt[1]/binwidth,rsquared])
    df = pd.DataFrame(results,columns=['D','N','Rsquared'])
    df['lagtime'] = lagtimelist
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"OneStateFit-diplacements.png"))
    plt.close('all')
    df.to_csv(os.path.join(os.path.split(filename)[0],"OneStateDiffusionAverages_gauss.csv"))

    gaussmean = df.iloc[0]#.mean()

    return pd.DataFrame(gaussmean[['D','N','Rsquared']]).transpose()


def makeMSD(filename):
    df_track = pd.read_csv(filename,sep=' ')
    df_track_array = fillMissingSteps(df_track)
    
    msd = []
    lagtimes = np.arange(300)+1
    for lag in lagtimes:
        df_displace = df_track_array[lag:] - df_track_array[:-lag]
        lag_average = df_displace[:,0].mean()
        df_displace = (df_displace[:,1]**2 + df_displace[:,2]**2)*0.067**2
        msd.append([lag_average,df_displace.mean(),df_displace.std(),len(df_displace)])
    msd = np.array(msd)

    def msd_fit(tau,D,C):
        return 4*D*tau + C

    fitrange = 20
    popt,pcov = curve_fit(msd_fit,msd[:fitrange,0],msd[:fitrange,1],p0=[1e-4,0])
    SSres = np.sum((msd[:fitrange,1] - msd_fit(msd[:fitrange,0],popt[0],popt[1]))**2)
    SStot = np.sum((msd[:fitrange,1] - np.mean(msd[:fitrange,1]))**2)
    rsquared = 1 - SSres/SStot

    df_output = pd.DataFrame()
    df_output['lagtime'] = msd[:40,0]
    df_output['D'] = msd[:40,1]/(4*msd[:40,0])
    df_output['Dmsd_fit'] = [popt[0]]*len(df_output)
    df_output.to_csv(os.path.join(os.path.split(filename)[0],"OneStateDiffusionAverages_MSD.csv"),sep=',',index=False)

    msdrange = 100
    plt.figure(figsize=(iw/3,iw/4))
    ax = plt.gca()
    ax2 = ax.twinx()
    ax.errorbar(msd[:msdrange,0],msd[:msdrange,1],yerr=msd[:msdrange,2]/np.sqrt(msd[:msdrange,3]),marker='x',linestyle=' ',label="D={:0.06f}".format(popt[0])+"$\si{\mu m}^2\si{s}^{-1}$")
    ax.plot(msd[:msdrange,0],msd_fit(msd[:msdrange,0],popt[0],popt[1]),'-',label="R$^2$={:0.02f}".format(rsquared))
    ax2.plot(msd[:msdrange,0],msd[:msdrange,3],'ro')
    ax.set_xlabel("tau [s]")
    ax.set_ylabel("MSD [\si{\mu m}$^2$]")
    ax2.set_ylabel("NumSteps",color='r')
    #ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.split(filename)[0],"OneStateFit-msd.png"))
    plt.close('all')

    return pd.DataFrame({'Dfirst': [msd[0,1]/(4*msd[0,0])], 'D': [popt[0]], 'Offset': [popt[1]], 'Rsquared': [rsquared]})



def oneStateFit(tracklist,celtype,temp,SR,amplitudef):
    print("*"*72)
    print("One State Fit")
    print("-"*30)
    count = 0
    #cols = ['CelType','Temperature','gaussD1','gaussD2','gaussA1','gaussA2','raddistD1','raddistD2','raddistA1','raddistA2']
    df = pd.DataFrame()
    for trackfile in tracklist:
        print(trackfile)
        try:
            msdout = makeMSD(trackfile)
        except RuntimeError:
            msdout = pd.DataFrame({'D': np.nan, 'Offset': np.nan, 'Rsquared': np.nan})
        try:
            dgauss = makeGauss(trackfile,amplitudef)
        except RuntimeError:
            dgauss = pd.DataFrame({'D1':[np.nan],'N1':[np.nan],'Rsquared':[np.nan]})
        try:
            raddist = makeRadialDistribution(trackfile,amplitudef)
        except RuntimeError:
            raddist = pd.DataFrame({'D1':[np.nan],'N1':[np.nan],'Rsquared':[np.nan]})
        middleman = pd.DataFrame({'CelType':[celtype[count]],'Temperature':[temp[count]]})
        dgauss.columns = ['gaussD1','gaussN1','gaussRsq']
        raddist.columns = ['raddistD1','raddistN1','raddistRsq']
        msdout.columns = ['msdDfirst','msdD1','msdOffset','msdRsq']
        saverdf = pd.concat([middleman,dgauss,raddist,msdout],axis=1)
        df = pd.concat([df,saverdf],ignore_index=True,axis=0)

        count += 1

    print("*"*72)
    df.to_csv("OneStateDiffusionSummary{:}.csv".format(SR))
    return

if __name__=="__main__":
    tracklist = []
    celtype = []
    temp = []
    SR = "_SR3.0"
    for dirname,dirlist,filelist in os.walk('.'):
        if "SingleStateAnalysis{:}".format(SR) in dirname:
            if os.path.isfile(os.path.join(dirname,'combinedTrack.txt')):
                tracklist.append(os.path.join(dirname,'combinedTrack.txt'))
                dirarray = os.path.normpath(dirname).split(os.path.sep)
                celtype.append(dirarray[0][:5])
                temp.append(int(dirarray[1][:2]))
    oneStateFit(tracklist,celtype,temp,SR)


