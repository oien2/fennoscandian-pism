#!/bin/bash
set -x -e 
GRID=20000
if [ $# -gt 0 ] ; then
  GRID="$1"
fi

lgmclim=Aclim_CCSM4_lgm_r1i1p1_180001-190012-clim

python ../run/create_fennoscandian_utm32n_grid.py -g $GRID fs_${GRID}m_grid.nc
for var in pr tas; do
    cdo remapbil,fs_${GRID}m_grid.nc ${var}_${lgmclim}.nc ${var}_${lgmclim}_fs_${GRID}m.nc
    ncks -A -v x,y fs_${GRID}m_grid.nc ${var}_${lgmclim}_fs_${GRID}m.nc
done

ncks -O pr_${lgmclim}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m.nc
ncks -A -v tas,tas_var tas_${lgmclim}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m.nc
ncrename -v pr,precipitation -v tas,air_temp -v pr_var,precipitation_var -v tas_var,air_temp_var ${lgmclim}_fs_${GRID}m.nc
# NOTE: we currently do NOT convert the variance variables
ncap2 -O -s "precipitation=precipitation/910*31556926;" ${lgmclim}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m.nc
ncatted -a units,precipitation,o,c,"m year-1" ${lgmclim}_fs_${GRID}m.nc

icefile=ice5g_v1.2_21.0k_10min
ncatted -a missing_value,,d,, ${icefile}.nc
cdo remapbil,fs_${GRID}m_grid.nc ${icefile}.nc ${icefile}_fs_${GRID}m.nc
ncks -A -v x,y fs_${GRID}m_grid.nc ${icefile}_fs_${GRID}m.nc
ncks -A -v orog ${icefile}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m.nc
python add_time_bounds.py ${lgmclim}_fs_${GRID}m.nc

# take number of days per month into account
cdo divc,12 -muldpy -timmean -divdpm ${lgmclim}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m_annual_mean.nc
ncks -A -v x,y fs_${GRID}m_grid.nc ${lgmclim}_fs_${GRID}m_annual_mean.nc
# This ignores the number of days per month
# cdo timmean ${lgmclim}_fs_${GRID}m.nc ${lgmclim}_fs_${GRID}m_annual_mean.nc
