#!/bin/bash

ncks -O rr_monthly_65y_50_75N_0_55E.nc merge_paleo.nc
ncrename -d lat,latitude -d lon,longitude -v lat,latitude -v lon,longitude merge_paleo.nc
ncks -A -v tg nc_tg_land_ocean_65y_50_75N_0_55E.nc merge_paleo.nc
ncrename -d month,time -v month,time  merge_paleo.nc
ncatted -a calendar,time,o,c,"none" -a units,time,o,c,"months since 1-1-1"  -a axis,time,o,c,"T" -a long_name,time,o,c,"time" merge_paleo.nc
ncatted -a units,rr,o,c,"mm month-1" -a units,tg,o,c,"Celsius" -a Conventions,global,o,c,"CF-1.6" merge_paleo.nc
