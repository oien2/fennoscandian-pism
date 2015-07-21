#!/bin/bash
# first github lesson

# download PISM*.mat
matlab -nodesktop -nojvm -nosplash -r createNCDFSCRIPT.m

# run preprocess.py
python preprocess.py
