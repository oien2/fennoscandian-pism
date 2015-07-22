#!/bin/bash

xmin=-22500
ymin=5547500
xmax=2387500
ymax=8247500


for GRID in 5000; do
    for var in air_temp precipitation; do
    outfile=${var}_${GRID}m.nc
    gdalwarp -overwrite -r bilinear -dstnodata 20 -s_srs EPSG:4326 -t_srs EPSG:32632 -te $xmin $ymin $xmax $ymax -tr $GRID $GRID -of netCDF NETCDF:modernclimate.nc:${var} $outfile
    done
    python merge_climate.py air_temp_${GRID}m.nc precipitation_${GRID}m.nc fscs_climate_${GRID}m_MM.nc
    cdo timmean fscs_climate_${GRID}m_MM.nc fscs_climate_${GRID}m.nc
    ncatted -a units,time,o,c,"month" fscs_climate_${GRID}m.nc
done
