#!/bin/bash
# first github lesson

# remove existing file because Matlab can't overwrite it
rm -f modernclimate.nc
# run Matlab to create temp/precip file
matlab -nodesktop -nojvm -nosplash -nodisplay < createNCDFSCRIPT.m

# run preprocess.py
python preprocess.py
