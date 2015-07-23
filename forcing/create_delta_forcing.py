#!/usr/bin/env python
# Copyright (C) 2015 Andy Aschwanden

import numpy as np
from netCDF4 import Dataset as CDF
from argparse import ArgumentParser

if __name__ == "__main__":
    # Set up the option parser
    description = '''Merge climate data.'''
    parser = ArgumentParser()
    parser.description = description

    parser.add_argument("OUTPUTFILE", nargs=1, help="output NetCDF file name", default="out.nc")
    parser.add_argument("--delta_T", dest="delta_T", type=float,
                        help="temperature offset in Kelvin [default=0]", default=0)
    parser.add_argument("--frac_P", dest="frac_P", type=float,
                        help="precipitation fraction scaling [default=1]", default=1)
    parser.add_argument("--delta_SL", dest="delta_SL", type=float,
                        help="sea-level relative to present-day [default=0]", default=0)

    options = parser.parse_args()
    delta_T = options.delta_T
    frac_P = options.frac_P
    delta_SL = options.delta_SL
    
    nc = CDF(options.OUTPUTFILE[0], 'w',format='NETCDF3_64BIT')

    nt = 1
    n_bounds = 2

    nc.createDimension("time", size=nt)
    nc.createDimension("n_bounds", size=2)
    
    var = 'time'
    var_out = nc.createVariable(var, 'f', dimensions=("time"))
    var_out.units = 'years'
    var_out.calendar = 'none'
    var_out.standard_name = 'time'
    var_out.axis = "T"
    var_out.bounds = 'time_bounds'
    var_out[:] = 0

    var = 'time_bounds'
    var_out = nc.createVariable(var, 'f', dimensions=("time", "n_bounds"))
    var_out[:] = [0, 0.1]

    var = 'delta_T'
    var_out = nc.createVariable(var, 'f', dimensions=("time"))
    var_out.units = "K"
    var_out[:] = delta_T

    var = 'frac_P'
    var_out = nc.createVariable(var, 'f', dimensions=("time"))
    var_out[:] = frac_P

    var = 'delta_SL'
    var_out = nc.createVariable(var, 'f', dimensions=("time"))
    var_out.units = "meters"
    var_out.standard_name = "global_average_sea_level_change"
    var_out[:] = delta_SL

    from time import asctime
    historystr = 'Created ' + asctime() + '\n'
    nc.history = historystr
    nc.Conventions = 'CF-1.6'
    
    nc.close()
