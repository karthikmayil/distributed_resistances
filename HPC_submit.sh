#!/bin/sh
#
# Simple "Hello World" submit script for Slurm.
#
# Replace <ACCOUNT> with your account name before submitting.
#
#SBATCH --account=cheme
#SBATCH --job-name=NMC_sampling_HV_Fading
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00
#SBATCH --mem-per-cpu=1gb
 
# run the fortran code
gfortran *.f95
./a.out

# remove extraneous files
rm ./a.out
rm *.mod
rm slurm*
rm *.f95
rm *.56
rm *.sh
rm *_Pos*
