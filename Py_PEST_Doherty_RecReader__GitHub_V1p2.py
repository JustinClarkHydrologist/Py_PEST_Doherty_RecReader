"""     Python PEST Post Processor to Read Raw RMR Output File and Create a Pandas DataFrame Summizing Run Times
             Started  on  03/03/2019
             Last Updated 07/21/2025 (July 21st, I am from the US)
@author: Justin A. Clark
This program takes the raw output text files from PEST and creates a Pandas DataFrame and graphs.
   -Intended to work for John Doherty PEST .rec files
   -Pandas is the main library
   -The final output figures are saved as .png format
   -Name of PEST case is supplied as a command line argument (the pest filename with no extension).

"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#
##EXTRACT THE NAME OF THE PEST RUN FROM THE COMMAND LINE ARGUMENT and assign it to the .rec file
PESTcase = sys.argv[1]            ########PESTcase = "phx_rch_v3d_svda"
RECfile = PESTcase + ".rec"

#
##READ THE .rec and .rmr FILES USING READ_CSV
df = pd.read_csv(RECfile, delimiter = "/s", engine = 'python', header = None)
ColNam = "RecOut"  ##This column that has the data I want to parse
df.rename( columns={0 :ColNam}, inplace=True )

#
##PREPARE A DATAFRAME (MATRIX) OF REC FILE DATA
ColNam = "first"  ##This is the new column with the first word of each line
df[ColNam] = df.stack().str.split(n=1).str[0].unstack()  ##This gets the first word in each string, copied from online

#
##PARSE THE STARTING PHI VALUES FOR EACH ITERATION
ParseStr = "Contribution"
df2 = pd.DataFrame(df['RecOut'].loc[df[ColNam] == ParseStr])
df2['PhiCont'] = df2['RecOut'].astype(str).str.split().str[-1]
df2['Grp'] = df2['RecOut'].astype(str).str.split().str[-3]
df2['Grp'] = df2['Grp'].str.replace('\"','')

#
##EXTRACT THE NAMES OF THE PARAMETER GROUPS, COU
groups = list(set(df2.Grp))
GrpCnt = len(groups)
groups = list(df2.Grp[0:GrpCnt])

#
##THIS STEP REMOVES THE FIRST SET OF RESULTS, BAD DATA
df3 = df2.tail(-GrpCnt)
IterCnt = int(len(df3) / GrpCnt)

#
##CREATE AN EMPTY DATAFRAME TO HOLD THE RESULTS, WITH A USABLE COL NAME
df5 = pd.DataFrame(IterCnt*['0'])
df5.columns = ['IterNo']
df5['IterNo'] = range(1,IterCnt+1)

#
##LOOP THROUGH THE PARAMETER GROUPS TO GET THE PHI CONTRIBUTIONS
for i,location in enumerate(groups):
     df4 = df3['PhiCont'].loc[df3['Grp'] == location]
     df4 = pd.to_numeric(df4)
     df4 = df4.reset_index()
     df4 = df4.drop("index", axis = 1)
     df4.columns.values[0] = location
     df5[location] = df4

#
##CALCULATE THE NET PHI, NOT EXTRACTED MANUALLY, not used in the code
df5['NetPhi'] = df5[list(df5.columns)].sum(axis=1)


#
##GRAPH IT UP!
df5['YVals'] = pd.to_numeric(IterCnt*['0'])
df5['Bot'] = pd.to_numeric(IterCnt*['0'])

ncol = 1
if GrpCnt > 9: ncol = 2
if GrpCnt > 20: ncol = 3

for x in groups:
     df5['Bot'] = df5['YVals']
     df5['YVals'] = df5['Bot'] + df5[x]

     plt.bar(df5['IterNo'], df5['YVals']-df5['Bot'], bottom = df5['Bot'])
     plt.plot(df5['IterNo'], df5['YVals'], "k", ls = "--", label = '_nolegend_')

#MaxPhi = int(df5.Vals.max())
#Ticks = pd.to_numeric(10)
#Interval = int(MaxPhi/Ticks)

plt.xlabel("Iteration No.")
plt.ylabel("PEST Phi (End Value)")

#plt.legend()
#plt.legend(groups)
plt.legend(groups,loc = 'upper right', ncol = ncol)

fig = plt.gcf()
fig.suptitle('PEST Case: ' + PESTcase, fontsize = 'xx-large')

##plt.show()   ###plt.show() here stopped the program while it was running, python graphic output but program doesn't move past this step.

#
##SAVE THE FIGURE: outname = 'Hydrographs_GWSI_Manual_' + str(i) + '.png'
outname = PESTcase + str('__Phi_Out_wide.png')
fig.savefig(outname, dpi = 600, bbox_inches='tight', pad_inches=.1)
outname = PESTcase + str('__Data_Table.csv')
df5 = df5.drop([df5.columns[-2] , df5.columns[-1]] , axis='columns')
df5.to_csv(outname, index=False)
