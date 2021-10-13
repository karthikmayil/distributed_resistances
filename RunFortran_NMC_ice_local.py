######################################
#### IMPORT NECESSARY PACKAGES #######
######################################

import numpy as np                          # Useful for numerical calculations on an array
import os                                   # Used for changing directories and open files with folders
import pandas as pd                         # Used to read csv files
import matplotlib.pyplot as plt             # Used for making plots
import sobol_seq                              # Sobol Package used to generate Sobol Sequence
import math
from matplotlib.ticker import FormatStrFormatter
import sys
from subprocess import call                 # Allows Python to call shell script
import shutil
import re
import glob
import random
from operator import itemgetter   			# Allows us to find groups of consecutive numbers
from itertools import groupby
import scipy.stats as stats
from scipy.optimize import minimize
from scipy.special import erf     			# error function (erf)


###### DEFINE HELPER FUNCTIONS ######
### Run_Model Function is no longer necessary
def Run_Model(Input_Parameters, Model_Folder, Shell_Script):

    # PASS PARAMETERS TO SHELL SCRIPT
    cmd = ['bash', Shell_Script]
    for param in Input_Parameters:
        cmd.append(str(param))

    # RUN MODEL USING SHELL SCRIPT
    p = call(cmd)               # run model


def sed(pattern, replace, source, dest=None, count=0):
    """Reads a source file and writes the destination file.

    In each line, replaces pattern with replace.

    Args:
        pattern (str): pattern to match (can be re.pattern)
        replace (str): replacement str
        source  (str): input filename
        count (int):   number of occurrences to replace
        dest (str):    destination filename, if not given, source will be over written.
    """

    fin = open(source, 'r')
    num_replaced = count

    if dest:
        fout = open(dest, 'w')
    else:
        fd, name = mkstemp()
        fout = open(name, 'w')

    for line in fin:
        out = re.sub(pattern, replace, line)
        fout.write(out)

        if out != line:
            num_replaced += 1
        if count and num_replaced > count:
            break
    try:
        fout.writelines(fin.readlines())
    except Exception as E:
        raise E

    fin.close()
    fout.close()

    if not dest:
        shutil.move(name, source)



def sobol(bounds, num_points):
    '''This function returns a sobol sequence, given bounds for each
    parameter and a total number of points. Bounds for each parameter
    must be entered in a list as follows:
    bounds = [ [lwr_bnd1, upr_bnd1], [lwr_bnd2, upr_bnd2], ... ]'''

    number_of_variables = len(bounds)

    # Sobol Sequence is pseudo random from 0-1, therefore,
    # we must scale the Sobol Sequence to the bounds specified
    Starting_Sobol = sobol_seq.i4_sobol_generate(number_of_variables, num_points)
    Modified_Sobol = []

    for points in Starting_Sobol:  # Iterate through each Sobol point

        New_Sobol_Point = []  # New points is list because it can have multiple dimensions

        for i in range(number_of_variables):  # Go through each dimension of the Sobol point

            add = bounds[i][0]                  # Amount to shift Sobol point in respective dimension
            diff = bounds[i][1] - bounds[i][0]  # Length to scale Sobol point in respective dimension
            temp = add + points[i] * diff       # Modify Sobol point in respective dimension
            New_Sobol_Point.append(temp)        # New position to the new Sobol point

        Modified_Sobol.append(New_Sobol_Point)  # Add all the modified Sobol points to a list and return

    return(Modified_Sobol)

#### NAVIGATE TO APPROPRIATE DIRECTORY ####

# MAKE THE SOBOL POINTS
#                    # cbcb,     spaspa
sobol_pts = sobol([[1.0, 1.0], [10.8,10.8], [0.5, 0.5], [0, 300]], 4) # 10**12 = 4096





####
#current_rates = np.linspace(5,360,10)
#current_rates = [5.0, 10.0]#, 20.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]
#print(current_rates)
#exit()

                #C/10       #C/5          #C/2          #C/1
#cspec_list = [-37.488, -74.98271368, -183.8229029, -360.5902897]
#cspec_list = [74.98271368]


###################################################
#################### FILE LIST ####################
###################################################
fortran_code = 'NMC111_Elect_Agg_Ice_Temp_x.f95'
fortran_code_values = 'NMC111_Elect_Agg_Ice_Temp_x.f95'
HPC_script  = 'HPC_submit.sh'


####### MAKE THIS SHELL SCRIPT ########
#shell_script = 'Shell_LiV3O8_Python.sh'

text_to_replace = ['frfr', 'dfcdfc', 'rkrk', 'rcdrcd']

C_rate_list = [0.5]

# C_rate_list = [2.0]

HPC = False # variable to indicate if the simulations are being run on the cluster or locally

###################################################
## CREATE NEW DIRECTORIES FOR EACH CURRENT RATE ###
###################################################
cwd = os.getcwd() # current working directory

for ii,cs in enumerate(C_rate_list):
    os.chdir(cwd)

    cwd_new = cwd + '/'  + str(cs)+'C'
    try:
            os.mkdir(cwd_new)
    except:
        pass

    for oo, sb in enumerate(sobol_pts):

        os.chdir(cwd_new)

        try:
            os.mkdir(cwd_new + '/' + '/' + str(oo))
        except:
            pass

        value_dir = str(oo)
        # loop thru the fortran code replacing the dummy values with the desired values

        text_values = sb

        _source = cwd + '/' + fortran_code
        _source_HPC = cwd + '/' + HPC_script

        _dest = cwd + '/' + 'fortran_temp_' + str(100) + '.f95'
        _dest_HPC = cwd + '/' + 'HPC_temp_' + str(100) + '.sh'
        sed('crcr', str(cs), _source, _dest )
        sed('crcr', str(cs), _source_HPC, _dest_HPC )
        _source = _dest
        _source_HPC = _dest_HPC

        for o, text in enumerate(text_to_replace):
        	#print o, text, str(text_values[o])
        	# loop thru fortran code
            _dest = cwd + '/' + 'fortran_temp_' + str(o) + '.f95'
            _dest_HPC = cwd + '/' + 'HPC_temp_' + str(o) + '.sh'
            sed(text, str(text_values[o]), _source, _dest )
            sed(text, str(text_values[o]), _source_HPC, _dest_HPC)
            _source_HPC = _dest_HPC
            _source = _dest

        # move the files with values to the corresponding directory
        #print(value_dir + '/')
        shutil.move(_source, value_dir + '/' +  fortran_code_values)
        shutil.move(_source_HPC, value_dir + '/' + HPC_script)
        # navigate to the directory containing the fortran code with values
        os.chdir(value_dir)


        if HPC == False:
        # complile and run the fortran code
            p = call(['gfortran', fortran_code_values])
            p = call(['./a.out'])

        if HPC == True:
    # if running the fortran on the cluster
    #if oo >= 0:
            p = call(['sbatch', HPC_script])

        for fl in glob.glob('*fort*'):
            os.remove(fl)

        for fl in glob.glob('*.mod*'):
            os.remove(fl)

        for fl in glob.glob('*out*'):
            os.remove(fl)

        # for fl in glob.glob('*Position*'):
        #    os.remove(fl)


# remove all temporary files
os.chdir(cwd)
for fl in glob.glob('*temp*'):
    os.remove(fl)

# create a dataframe from the sobol points
# add a column linking the folder number to the sobol points
# make folder column first column for better readability
sobol_df = pd.DataFrame(np.vstack(sobol_pts))
sobol_df.columns = [ 'fr', 'dfc', 'rk', 'spa']
# sobol_df.columns = [ 'rk']
sobol_df['folders'] = pd.Series(range(0,len(sobol_df)), index = sobol_df.index)
cols = sobol_df.columns.tolist()
cols = cols[-1:] + cols[:-1]
sobol_df = sobol_df[cols]


# write a text file correlating the folder structure with the Sobol Points
headers = sobol_df.columns.tolist() #['folder', 'Diff', 'k_rxn', 'c_sat', 'i0']
add = ''
for h in range(0,len(headers)):
    add += '{0:12s}'.format( headers[h] )

# save a file correlating the folder structure with the Sobol Points
np.savetxt('SobolPts.txt', sobol_df, delimiter = ' ', fmt = '%-11.6g', header = add, comments='')



#########################################
############# YETI FILE #################
#########################################
'''
#!/bin/sh
# Directives


#PBS -N curr_lll_V3O8
#PBS -W group_list=yeticheme
#PBS -l nodes=1:ppn=1,walltime=11:50:00,mem=2gb
#PBS -M nwb2112@columbia.edu
#PBS -m n
#PBS -V

#PBS -o localhost:~/temp
#PBS -e localhost:~/temp

cd $PBS_O_WORKDIR

# run the fortran code
gfortran *.f95
./a.out

# remove extraneous files
rm ./a.out
rm *.mod
'''
