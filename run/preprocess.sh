#!/bin/bash
# first github lesson

echo "Downloading ETOPO1"
etopo_bedrock=ETOPO1_Bed_g_gmt4
etopo_surface=ETOPO1_Ice_g_gmt4
wget -nc https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/${etopo_bedrock}.grd.gz
wget -nc https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/ice_surface/grid_registered/netcdf/${etopo_surface}.grd.gz
echo "Unpacking ETOPO1"
gunzip -k -f ${etopo_bedrock}.grd.gz
gunzip -k -f ${etopo_surface}.grd.gz
echo 


Nlim=74.8 #74.0 # degrees
Slim=50.0 #48.5
Wlim=-1.0 #-2.75
Elim=53.0 #45.25

xmin=-22500
ymin=5547500
xmax=2387500
ymax=8247500


for GRID in 20000 10000 5000; do
    outfile=pism_FennoScandian_${GRID}m.nc
    gdalwarp -overwrite -r average -s_srs EPSG:4326 -t_srs EPSG:32632 -te $xmin $ymin $xmax $ymax -tr $GRID $GRID -of netCDF ${etopo_bedrock}.grd ${etopo_bedrock}_${GRID}m.nc
    gdalwarp -overwrite -r average -s_srs EPSG:4326 -t_srs EPSG:32632 -te $xmin $ymin $xmax $ymax -tr $GRID $GRID -of netCDF ${etopo_surface}.grd ${etopo_surface}_${GRID}m.nc
    ncks -O ${etopo_bedrock}_${GRID}m.nc $outfile
    ncrename -O -v Band1,topg $outfile $outfile
    ncatted -a standard_name,topg,o,c,"bedrock_altitude" -a units,topg,o,c,"meters" $outfile
    ncks -A ${etopo_surface}_${GRID}m.nc $outfile
    ncrename -O -v Band1,usurf $outfile $outfile
    ncatted -a standard_name,usurf,o,c,"surface_altitude" -a units,usurf,o,c,"meters" $outfile
done
