# Import modules
from matplotlib.pylab import *
import matplotlib.pyplot as plt
import numpy
import os
import csv
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from ASS_utilities import ReadObsFlowsAss
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()

def Results(obs_file, IssueDate, Startdate, Enddate, Ass_folder, rch_ID):

    #Getting the observed data and identify reach(es)
    if os.path.isfile(obs_file):
        Q_obs = ReadObsFlowsAss(obs_file)
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        reachID = []
        reachID.append(Q_obs[0,3])
        for i in range(1,len(Q_obs)):
            if Q_obs[i,3] != reachID[-1]:
                reachID.append(Q_obs[i,3])
    else:
        reachID = [rch_ID]

    for n in range(0,len(reachID)):

        #Routed simulation data
        x3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Output.csv', delimiter=',')
        P3 = genfromtxt(Ass_folder + os.sep + 'Assimilation_Cov.csv', delimiter=',')
        q_ass = x3[int(reachID[n])-1,:]
        std_ass = P3[int(reachID[n])-1,:]

        #Creating the bounds
        up_bound_ass = q_ass+2*std_ass
        low_bound_ass = numpy.zeros([len(q_ass)])
        for j in range (0,len(q_ass)):
            if q_ass[j]-2*std_ass[j]>0:
                low_bound_ass[j] = q_ass[j]-2*std_ass[j]
            else:
                low_bound_ass[j] = 0

        timestep = (Enddate-Startdate+1)/len(q_ass)

        # Create plot
        dates = numpy.arange(Startdate, Startdate + len(q_ass)/(1/timestep),timestep)
        fig = plt.figure()
        plt.title('Assimilation results for reach  '+str(int(reachID[n])), fontsize=12)
        plt.ylabel('Discharge [$m^3/s$]')
        p1, = plt.plot_date(dates, q_ass, linestyle='-',color='green', marker = 'None')
        plt.plot_date(dates, low_bound_ass, linestyle='--', color = 'green',marker = 'None')
        plt.plot_date(dates, up_bound_ass, linestyle='--', color = 'green',marker = 'None')
        if os.path.isfile(obs_file):
            # Extract obsdata for current reachID
            obsdata = Q_obs[find(Q_obs[:,3]==int(reachID[n])),:]
            if sum(obsdata[:,0] >= Startdate) > 0:
                obsdata = obsdata[find(obsdata[:,0] >= Startdate),:]
            if sum(obsdata[:,0] <= Enddate-8) > 0:
                obsdata = obsdata[find(obsdata[:,0] <= Enddate-8),:]
            obstimes = obsdata[:,0]
            obs_dates = obstimes
            p2, = plt.plot_date(obs_dates, obsdata[:,1], color='red', marker = '.')
            plt.legend([p1,p2],['Assimilated Run','Observed'],loc='upper left')
        plt.legend(loc=0)
        grid(True)
        grid(True)
        ax1 = fig.add_subplot(111)
        ax1.fill_between(dates, low_bound_ass, up_bound_ass, color='green',alpha=.3)
        p = []
        for i in range(-30,9):
            p.append(str(i))
        p[30]= str(num2date(Enddate-8))[0:10]
        plt.xticks(numpy.arange(dates[0],dates[-1]+1), p, size='xx-small')
        plt.xlim([Startdate+20, Enddate])
        plt.ylim([0,up_bound_ass[-1]])
        figname = Ass_folder + os.sep + 'Assimilation_Results_reach' + str(int(reachID[n])) + '_'+ IssueDate +'.pdf'
        plt.savefig(figname)
        plt.show()