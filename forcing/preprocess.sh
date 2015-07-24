#!/bin/bash

# Adjust bounding box to accomodate 20km grids
xmin=$((-22500 - 15000)) 
ymin=$((5547500 - 10000))
xmax=$((2387500 + 15000))
ymax=$((8247500 + 10000))

for GRID in 20000 5000; do
    for var in air_temp precipitation; do
    outfile=${var}_${GRID}m.nc
    gdalwarp -overwrite -r bilinear -dstnodata 20 -s_srs EPSG:4326 -t_srs EPSG:32632 -te $xmin $ymin $xmax $ymax -tr $GRID $GRID -of netCDF NETCDF:modernclimate.nc:${var} $outfile
    done
    python merge_climate.py air_temp_${GRID}m.nc precipitation_${GRID}m.nc fscs_climate_${GRID}m_MM.nc
    # convert from water equiv. to ice equiv.
    ncap2 -O -s "precipitation=precipitation/.910;" fscs_climate_${GRID}m_MM.nc fscs_climate_${GRID}m_MM.nc
    cdo timmean fscs_climate_${GRID}m_MM.nc fscs_climate_${GRID}m.nc
    ncatted -a units,time,o,c,"month" fscs_climate_${GRID}m.nc
    ncap2 -O -s "precipitation=precipitation*12*0.001; air_temp=air_temp+273.15" fscs_climate_${GRID}m.nc fscs_climate_${GRID}m_alt_units.nc
    ncatted -a units,precipitation,o,c,"m year-1" -a units,air_temp,o,c,"K" fscs_climate_${GRID}m_alt_units.nc
done

# Create delta forcing
python create_delta_forcing.py --frac_P 0.5 --delta_T -7 --delta_SL -120 delta_P_0.5_T_m7K_SL_m120m.nc
