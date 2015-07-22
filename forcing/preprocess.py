#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 20:34:57 2014
Imports input data .nc files and preprocesses for PISM
@author: lichtne2, oien2
"""

import netCDF4
import pyproj
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import pylab

# Import data and store variables
print('Importing files ...')


daymonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
climdata = netCDF4.Dataset('modernclimate.nc', 'r') 
#prsndata = netCDF4.Dataset('precip.mon.ltm.nc', 'r') #snow precip
#snmdata = netCDF4.Dataset('precip.mon.ltm.nc', 'r')   #snow melt
topgdata = netCDF4.Dataset('ETOPO1_Bed_g_gmt4.grd', 'r')
#thkdata = netCDF4.Dataset('PMIP3IceSheet/pmip3_21k_orog_diff_v0.nc', 'r') # use this (diff in ice sheet thickness$ from present? or ICE-5G ice thickness?)

#daymonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] #commented out to not forget how to set this up
#tsdata = netCDF4.Dataset('temp-mon.txt', 'r') # look into preprocess_v9 or earlier for the original call files.nc
#prdata = netCDF4.Dataset('precip-mon.txt', 'r')
#prsndata = netCDF4.Dataset('PMIP3NCAR/prsn_Aclim_CCSM4_lgm_r1i1p1_180001-190012-clim.nc', 'r')
#snmdata = netCDF4.Dataset('PMIP3NCAR/snm_LIclim_CCSM4_lgm_r1i1p1_180001-190012-clim.nc', 'r')
#topgdata = netCDF4.Dataset('ETOPO1/ETOPO1_Bed_g_gmt4.grd', 'r')
#thkdata = netCDF4.Dataset('PMIP3IceSheet/pmip3_21k_orog_diff_v0.nc', 'r') # use this (diff in ice sheet thickness from present? or ICE-5G ice thickness?)

#latlon
lon = climdata.variables['lon'][:]
lat = climdata.variables['lat'][:]

# surface temp
ts = climdata.variables['air_temp'][:]
ts = np.average(ts,axis=0,weights=daymonths) # Averages 12-month temp data --> yearly data (can I do this -- months are different lengths!)

# precip # pism name = prdata.variables['matlab name'][:]
pr = (climdata.variables['precipitation'][:])  
pr = np.average(pr,axis=0,weights=daymonths) # Averages 12-month temp data --> yearly data

# snowfall flux
#prsn = prsndata.variables['prsn'][:]*3600*24*365 # Convert from [kg m-2 s-1] to [kg m-2 yr-1]
#prsn = np.average(prsn,axis=0,weights=daymonths) # Averages 12-month temp data --> yearly data

# snow melt
#snm = snmdata.variables['snm'][:]*3600*24*365 # Convert from [kg m-2 s-1] to [kg m-2 yr-1]
#snm = np.average(snm,axis=0,weights=daymonths) # Averages 12-month temp data --> yearly data

# climate mass balance calculated from snowfall and snow melt
#cmb = prsn - snm

# ice thickness 21ka
#thk = thkdata.variables['orog_diff'][:] # We need modern thk, too, which we then add to this file!!!!!!!
#latthk = thkdata.variables['lat'][:] # thk is on different resolution grid
#lonthk = thkdata.variables['lon'][:]
#thk = thk.clip(min=0) # get rid of negative thicknesses (this is a problem for this input data set...find another?)

# topography
topg = topgdata.variables['z'][:]
lat2 = topgdata.variables['y'][:] # topg is on different resolution grid
lon2 = topgdata.variables['x'][:]


## Clip variables to area of interest in N Europe
print('Clipping to manageable area in N Europe ...')

Nlim = 74.8 #74.0 # degrees
Slim = 50.0 #48.5
Wlim = -1.0 #-2.75
Elim = 53.0 #45.25

# Clip GCM data
cliplonind = [i for i,v in enumerate(lon) if (v < Elim and v > Wlim)]
cliplatind = [i for i,v in enumerate(lat) if (v < Nlim and v > Slim)]

lonclip = lon[cliplonind]
latclip = lat[cliplatind]

tsclip = ts[cliplatind, :]
tsclip = tsclip[:,cliplonind]

prclip = pr[cliplatind, :]
prclip = prclip[:,cliplonind]

#cmbclip = cmb[cliplatind, :]; cmbclip = cmbclip[:,cliplonind] #climate mass balance - not for sensitivity

# Clip topg data, which has different resolution
cliplonind = [i for i,v in enumerate(lon2) if (v < Elim and v > Wlim)]
cliplatind = [i for i,v in enumerate(lat2) if (v < Nlim and v > Slim)]

lon2clip = lon2[cliplonind]
lat2clip = lat2[cliplatind]
topgclip = topg[cliplatind, :]
topgclip = topgclip[:,cliplonind]

# Clip thk data, which has different resolution
#cliplonind = [i for i,v in enumerate(lonthk) if (v < Elim and v > Wlim)]
#cliplatind = [i for i,v in enumerate(latthk) if (v < Nlim and v > Slim)]

#lonthkclip = lonthk[cliplonind]
#latthkclip = latthk[cliplatind]
#thkclip = thk[cliplatind, :]; thkclip = thkclip[:,cliplonind]

# Test plot of clipped area in lon, lat -- uncomment for debugging
#plt.contourf(lon2clip,lat2clip,topgclip)
#plt.axis('equal')
#pylab.show()


# Transform from WGS1984 to UM Zone 32N projection
print('Reprojecting from WGS1984 to UTM Zone 32N ...')

longrid, latgrid = np.meshgrid(lonclip,latclip)
longrid2, latgrid2 = np.meshgrid(lon2clip,lat2clip) 
#lonthkgrid, latthkgrid = np.meshgrid(lonthkclip,latthkclip)
wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
utm32=pyproj.Proj("+init=EPSG:32632") # UTM Zone 32N for Norway 

x, y = pyproj.transform(wgs84, utm32, longrid, latgrid)
x2, y2 = pyproj.transform(wgs84, utm32, longrid2, latgrid2)
#x3, y3 = pyproj.transform(wgs84, utm32, lonthkgrid, latthkgrid)

# Test plot of clipped area in UTM -- uncomment for debugging
#plt.contourf(x2,y2,topgclip) # can change this to additional variables to make sure they are working such as precip
#plt.axis('equal')
#pylab.show()


# Interpolate to regularly spaced UTM data
print('Interpolating onto regularly spaced 5 km grid ...')
Nlim = 8250000 # meters; determined visually from plt.contourf
Slim = 5550000
Wlim = -20000
Elim = 2390000
grdspc = 5000

lin_x = np.arange(Wlim,Elim,grdspc)
lin_y = np.arange(Slim,Nlim,grdspc)
grid_x, grid_y = np.meshgrid(lin_x, lin_y)

grid_ts = griddata((np.ndarray.flatten(x), np.ndarray.flatten(y)), np.ndarray.flatten(tsclip), (grid_x, grid_y))
grid_pr = griddata((np.ndarray.flatten(x), np.ndarray.flatten(y)), np.ndarray.flatten(prclip), (grid_x, grid_y))
#grid_cmb = griddata((np.ndarray.flatten(x), np.ndarray.flatten(y)), np.ndarray.flatten(cmbclip), (grid_x, grid_y), method='cubic')
#grid_thk = griddata((np.ndarray.flatten(x3), np.ndarray.flatten(y3)), np.ndarray.flatten(thkclip), (grid_x, grid_y), method='cubic')
grid_topg = griddata((np.ndarray.flatten(x2), np.ndarray.flatten(y2)), np.ndarray.flatten(topgclip), (grid_x, grid_y))
grid_lon = griddata((np.ndarray.flatten(x2), np.ndarray.flatten(y2)), np.ndarray.flatten(longrid2), (grid_x, grid_y))
grid_lat = griddata((np.ndarray.flatten(x2), np.ndarray.flatten(y2)), np.ndarray.flatten(latgrid2), (grid_x, grid_y))

# Test plot of gridded area in UTM -- uncomment for debugging
#plt.contourf(grid_x,grid_y,grid_topg)
#plt.axis('equal')
#pylab.show()

# Export data to PISM-ready netCDF file
print('Exporting PISM-ready data file in this directory ...')

# import sys
# sys.exit(0)
# grid_ts2 = grid_ts[np.newaxis,:,:]
# grid_ts2[np.isnan(grid_ts2)] = 0
# grid_pr2 = grid_pr[np.newaxis,:,:]
# grid_pr2[np.isnan(grid_pr2)] = 0

grid_ts = grid_ts[np.newaxis,:,:]
grid_ts[np.isnan(grid_ts)] = 0
grid_pr = grid_pr[np.newaxis,:,:]
grid_pr[np.isnan(grid_pr)] = 0


#grid_cmb = grid_cmb[np.newaxis,:,:]; grid_cmb[np.isnan(grid_cmb)] = 0
#grid_thk = grid_thk[np.newaxis,:,:]; grid_thk = grid_thk.clip(min=0); grid_thk[np.isnan(grid_thk)] = 0 # get rid of negative and nan numbers...
grid_topg = grid_topg[np.newaxis,:,:]
grid_topg[np.isnan(grid_topg)] = 0
grid_lat = grid_lat[np.newaxis,:,:]
grid_lon = grid_lon[np.newaxis,:,:]

nc = netCDF4.Dataset('fscs_climate.nc', 'w', format='NETCDF3_64BIT')

# Set dimensions
time = nc.createDimension('time', None)
y = nc.createDimension('y', len(lin_y))
x = nc.createDimension('x', len(lin_x))

# Set variables
time = nc.createVariable('time','f8',('time',))
y = nc.createVariable('y','f8',('y',))
x = nc.createVariable('x','f8',('x',))
#climatic_mass_balance = nc.createVariable('climatic_mass_balance','f8',('time','y','x'))
temp = nc.createVariable('air_temp','f8',('time','y','x'))
lat = nc.createVariable('lat','f4',('time','y','x'))
lon = nc.createVariable('lon','f4',('time','y','x'))
precip = nc.createVariable('precipitation','f8',('time','y','x'))
#thk = nc.createVariable('thk','f8',('time','y','x'))
topg = nc.createVariable('topg','f8',('time','y','x'))
usurf = nc.createVariable('usurf','f8',('time','y','x'))

mapping = nc.createVariable('mapping','S1')


# Set variable attributes
nc.description = 'PISM input data based on ETOPO1 bedrock topography and PMIP3 NCAR temp and precip data for 21ka'
nc.history = 'Created Nov 2014 at UIUC'
nc.source = 'Derek Lichtner; Rachel Oien'

topg.units = 'meters'
precip.units = 'mm month-1'
usurf.units = 'meters'
#climatic_mass_balance.units = 'kg m-2 year-1'
temp.units = 'Celsius'
lat.units = 'degreeN'
lon.units = 'degreeE'
x.units = 'meters'
y.units = 'meters'
#thk.units = 'meters'
time.units = 'years since 01-01-01 00:00:00.0'
time.calendar = 'gregorian'

topg.grid_mapping = "mapping"
precip.grid_mapping = "mapping"
#climatic_mass_balance.grid_mapping = "mapping"
temp.grid_mapping = "mapping"
#thk.grid_mapping = "mapping"
lat.grid_mapping = "mapping"
lon.grid_mapping = "mapping"


topg.standard_name = 'bedrock_altitude'
topg.long_name = 'Bedrock Topography'
precip.standard_name = 'lwe_precipitation'
precip.long_name = 'Precipitation Rate 21ka'
#climatic_mass_balance.standard_name = 'land_ice_surface_specific_mass_balance'
#climatic_mass_balance.long_name = 'Surface Mass Balance'
temp.standard_name = 'ice_surface_temp'
temp.long_name = 'Annual Mean Surface Temperature'
#thk.standard_name = 'land_ice_thickness'
#thk.long_name = 'Ice Thickness'
lat.standard_name = 'latitude'
lat.long_name = 'Latitude'
lon.standard_name = 'longitude'
lon.long_name = 'Longitude'
usurf.standard_name = 'surface_altitude'

mapping.ellipsoid = "WGS84";
#mapping.false_easting = 0.0; // double
#mapping.false_northing = 0.0; // double
mapping.grid_mapping_name = "transverse_mercator";
#mapping.latitude_of_projection_origin = 0.0; // double
#standard_parallel = 71.0; // double
#straight_vertical_longitude_from_pole = -39.0; // double


# Write variables #These may need to be commented out if they are not being used
time[:] = 0
x[:] = lin_x
y[:] = lin_y
topg[:] = grid_topg
usurf[:] = grid_topg
precip[:] = grid_pr
#climatic_mass_balance[:] = grid_cmb
temp[:] = grid_ts
#thk[:] = grid_thk
lat[:] = grid_lat
lon[:] = grid_lon

nc.close()
