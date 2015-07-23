#!/usr/bin/env python
# Copyright (C) 2015 Andy Aschwanden
#

import numpy as np
from argparse import ArgumentParser
from netCDF4 import Dataset as CDF


def create_variable_like(in_file, var_name, out_file, dimensions=None,
                         fill_value=-2e9):
    """Create a variable in an out_file that is the same var_name in
    in_file, except possibly depending on different dimensions,
    provided in dimensions.

    """
    var_in = in_file.variables[var_name]
    try:
        fill_value = var_in._FillValue
    except AttributeError:
        # fill_value was set elsewhere
        pass

    if dimensions is None:
        dimensions = var_in.dimensions

    dtype = var_in.dtype

    var_out = out_file.createVariable(var_name, dtype, dimensions=dimensions,
                                      fill_value=fill_value)
    copy_attributes(var_in, var_out)
    return var_out


def copy_attributes(var_in, var_out):
    """Copy attributes from var_in to var_out. Give special treatment to
    _FillValue and coordinates.

    """
    _, _, _, tdim = get_dims_from_variable(var_in.dimensions)
    for att in var_in.ncattrs():
        if att == '_FillValue':
            continue
        elif att == 'coordinates':
            if tdim:
                coords = '{0} lat lon'.format(tdim)
            else:
                coords = 'lat lon'
            setattr(var_out, 'coordinates', coords)

        else:
            setattr(var_out, att, getattr(var_in, att))

def get_dims_from_variable(var_dimensions):
    '''
    Gets dimensions from netcdf variable

    Parameters:
    -----------
    var: netCDF variable

    Returns:
    --------
    xdim, ydim, zdim, tdim: dimensions
    '''

    def find(candidates, collection):
        """Return one of the candidates if it was found in the collection or
        None otherwise.

        """
        for name in candidates:
            if name in collection:
                return name
        return None

    # possible x-dimensions names
    xdims = ['x', 'x1']
    # possible y-dimensions names
    ydims = ['y', 'y1']
    # possible z-dimensions names
    zdims = ['z', 'zb']
    # possible time-dimensions names
    tdims = ['t', 'time']

    return [find(dim, var_dimensions) for dim in [xdims, ydims, zdims, tdims]]


    
if __name__ == "__main__":
    # Set up the option parser
    description = '''Merge climate data.'''
    parser = ArgumentParser()
    parser.description = description

    # First file is precip, second is temperature
    parser.add_argument("INPUTFILE", nargs=2, help="input files containing temperature and precip")
    parser.add_argument("OUTPUTFILE", nargs=1, help="output NetCDF file name", default="out.nc")

    options = parser.parse_args()
    nc_temp = CDF(options.INPUTFILE[0], 'r')
    nc_precip = CDF(options.INPUTFILE[1], 'r')
    
    projection = "+init=epsg:32632"

    x_in = nc_temp.variables['x']
    y_in = nc_temp.variables['y']
    
    nc = CDF(options.OUTPUTFILE[0], 'w',format='NETCDF3_64BIT')

    # Number of month in file
    nt = 12
    # number of grid points in x- and y-direction
    nx = x_in.shape[0]
    ny = y_in.shape[0]

    ignore_variables_list = ('x', 'y', 'transverse_mercator')
    temp = np.zeros((nt, ny, nx))
    for k, var in enumerate(nc_temp.variables):
        if var not in ignore_variables_list:
            temp[k,::] = nc_temp.variables[var][:]
        
    precip = np.zeros((nt, ny, nx))
    for k, var in enumerate(nc_precip.variables):
        if var not in ignore_variables_list:
            precip[k,::] = nc_precip.variables[var][:]
    
    nc.createDimension("time", size=nt)
    nc.createDimension("x", size=nx)
    nc.createDimension("y", size=ny)

    create_variable_like(nc_temp, 'x', nc)
    nc.variables['x'][:] = x_in[:]
    create_variable_like(nc_temp, 'y', nc)
    nc.variables['y'][:] = y_in[:]
    
    var = 'time'
    var_out = nc.createVariable(var, 'f', dimensions=("time"))
    var_out.units = 'month'
    var_out.calendar = 'none'
    var_out.standard_name = 'time'
    var_out.axis = "T"
    var_out[:] = range(nt)

    var = 'precipitation'
    var_out = nc.createVariable(var, 'f', dimensions=("time", "y", "x"))
    var_out.units = "mm month-1";
    var_out[:] = precip

    var = 'air_temp'
    var_out = nc.createVariable(var, 'f', dimensions=("time", "y", "x"))
    var_out.units = "deg_C";
    var_out[:] = temp
    
    from time import asctime
    historystr = 'Created ' + asctime() + '\n'
    nc.history = historystr
    nc.proj4 = projection
    nc.Conventions = 'CF-1.6'
    
    nc.close()
    nc_temp.close()
    nc_precip.close()
