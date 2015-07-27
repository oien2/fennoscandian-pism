#!/bin/bash
# first github lesson

# remove existing file because Matlab can't overwrite it
rm -f modernclimate.nc
# run Matlab to create temp/precip file
matlab -nodesktop -nojvm -nosplash -nodisplay < createNCDFSCRIPT.m

#Starts the  preprocess_grid_NOAA.sh file
./preprocess_regrid_NOAA.sh

# run preprocess.py -- make sure this is running the correct preprocess script - names have changed
#python preprocess.py
