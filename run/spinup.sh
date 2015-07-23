#!/bin/bash

# Authors: Derek Lichtner and Rachel Oien

set -e  # exit on error

NN=4  # default number of processors
if [ $# -gt 0 ] ; then  # if user says "paramspawn.sh 8" then NN = 8
  NN="$1"
fi

GRIDLIST="{20000,10000,5000}"

## Set Pism executable and number of cpus
PISM_MPIDO="mpiexec -n"
PISM_EXEC=pismr

## Parse input arguments -- perhaps fix this to use tags? otherwise you can't omit intermediate arg
# Usage: ./spinup.sh inputfile.nc outputfile.nc gridkmsize startyr endyr regridfile

# Set grid size
COARSESKIP=10
MEDIUMSKIP=20
FINESKIP=50
FINESTSKIP=200
VDIMS="-Lz 4000 -Lbz 2000 -skip -skip_max "
COARSEVGRID="-Mz 101 -Mbz 11 -z_spacing equal ${VDIMS} ${COARSESKIP}"
MEDIUMVGRID="-Mz 201 -Mbz 21 -z_spacing equal ${VDIMS} ${MEDIUMSKIP}"
FINEVGRID="-Mz 201 -Mbz 21 -z_spacing equal ${VDIMS} ${FINESKIP}"
FINESTVGRID="-Mz 401 -Mbz 41 -z_spacing equal ${VDIMS} ${FINESTSKIP}"
HIGHRESPETSC=""
if [ "$2" == "20000" ]; then
  dx=$2
  myMx=122
  myMy=136
  vgrid=$COARSEVGRID
elif [ "$2" == "10000" ]; then
  dx=$2
  myMx=244
  myMy=272
  vgrid=$MEDIUMEVGRID
elif [ "$2" == "5000" ]; then
  dx=$2
  myMx=488
  myMy=544
  vgrid=$FINEVGRID
else
  echo "invalid second argument: must be in $GRIDLIST"
  exit
fi
GRID=$dx

# Get input file name
if [ -z "$3" ]
  then
    PISM_CLIMATENAME=fscs_climate_5000m.nc 
  else
    PISM_CLIMATENAME=$3
fi

# Get out file name
if [ -z "$4" ]
  then
    OUTNAME=fs_unnamed.nc # default output file name if non specified
  else
    OUTNAME=$4 #2nd input arg is output datafile name
fi



SKIP=10 # vertical res - no input arg; defaults to following
VDIMS="-Lz 4000 -Lbz 2000 -skip -skip_max "
vgrid="-Mz 101 -Mbz 11 -z_spacing equal ${VDIMS} ${SKIP}"

# Set run time of model
if [ -z "$5" ]
  then
    STARTIME=-10000 # Need to change this based  on how long you want to run the model 
  else
    STARTIME=$5
fi

if [ -z "$6" ]
  then
    ENDTIME=0
  else
    ENDTIME=$6
fi

PISM_DATANAME=pism_FennoScandian_${GRID}m.nc

RUNSTARTEND="-ys $STARTIME -ye $ENDTIME"

# Set regridding file (makes fine resoluton calcs faster by using interpolated vars from already completed coarser run) 
if [ -z "$7" ]
  then
    regridcommand=""
  else
    regridcommand="-regrid_file $7 -regrid_vars litho_temp,thk,enthalpy,tillwat,bmelt"
fi

PISM_DELTA_FILE=delta_P_0.5_T_m7K_SL_m120m.nc
### The following input args are set to defaults in this script:

## Climate coupling inputs
#COUPLER="-surface given -surface_given_file $PISM_DATANAME" # no climate forcing, just reads mass balance from input file (constant climate) # didn't work

COUPLER="-atmosphere given,lapse_rate,delta_T,frac_P -atmosphere_delta_T_file $PISM_DELTA_FILE -atmosphere_frac_P_file $PISM_DELTA_FILE -temp_lapse_rate 6 -atmosphere_lapse_rate_file $PISM_DATANAME -atmosphere_given_file $PISM_CLIMATENAME -surface pdd -ocean constant,delta_SL -ocean_delta_SL_file $PISM_DELTA_FILE"

#COUPLER='-surface simple'  #doesn't work

## Ice physics
#PHYS="-pseudo_plastic" # Perfectplastic physics
#PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0"
#PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0 -stress_balance ssa+sia -topg_to_phi 15.0,40.0,-300.0,700.0 -pseudo_plastic -pseudo_plastic_q 0.5 -till_effective_fraction_overburden 0.02 -tauc_slippery_grounding_lines"
# test 1: PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0 -energy none -stress_balance none"
#test 2: PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0 -stress_balance none"
#test 3:
#PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0"
#test 4: 
#PHYS="-calving ocean_kill -ocean_kill_file $PISM_DATANAME -sia_e 3.0 -stress_balance ssa+sia -topg_to_phi 15.0,40.0,-300.0,700.0 -pseudo_plastic -pseudo_plastic_q 0.5 -till_effective_fraction_overburden 0.02 -tauc_slippery_grounding_lines" # straight from greenland example, more advanced ice physics -- this will require some adjusting in future
#PHYS="-pik -calving eigen_calving -stress_balance ssa+sia -pseudo_plastic -tauc_slippery_grounding_lines"

# What is the 'right' calving thickness threshold???
PHYS='-bed_def lc -pik -calving thickness_calving,eigen_calving -eigen_calving_K 1e17 -thickness_calving_threshold 50 -sia_e 3.0 -stress_balance ssa+sia -topg_to_phi 15.0,40.0,-300.0,700.0 -pseudo_plastic -pseudo_plastic_q 0.5 -till_effective_fraction_overburden 0.02 -tauc_slippery_grounding_lines'
#PHYS='-bed_def lc -calving float_kill -sia_e 3.0'

## DIAGONSTIC AND OUTPUT FILES
TSNAME=ts_$OUTNAME
TSTIMES=$STARTIME:yearly:$ENDTIME
EXNAME=ex_$OUTNAME
EXSTEP=100
EXTIMES=$STARTIME:$EXSTEP:$ENDTIME
EXVARS="diffusivity,temppabase,bmelt,tillwat,velsurf_mag,velbase_mag,mask,thk,topg,usurf,climatic_mass_balance,climatic_mass_balance_cumulative"

DIAGNOSTICS="-ts_file $TSNAME -ts_times $TSTIMES -extra_file $EXNAME -extra_times $EXTIMES -extra_vars $EXVARS"

$PISM_MPIDO $NN $PISM_EXEC -i $PISM_DATANAME -bootstrap -Mx $myMx -My $myMy $vgrid $RUNSTARTEND $regridcommand $COUPLER $PHYS $DIAGNOSTICS -o $OUTNAME
