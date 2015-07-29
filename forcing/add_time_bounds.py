#!/usr/bin/env python

import os
from argparse import ArgumentParser
from dateutil import rrule
from dateutil.parser import parse
from datetime import datetime
import time
import numpy as np

try:
    import netCDF4 as netCDF
except:
    print "netCDF4 is not installed!"
    sys.exit(1)
NC = netCDF.Dataset
from netcdftime import utime

# Set up the option parser
parser = ArgumentParser()
parser.description = '''Script creates a time file with time and time
bounds that can be used to determine to force PISM via command line
option -time_file'''
parser.add_argument("FILE", nargs='*')
parser.add_argument("-p", "--periodicity", dest="periodicity",
                    help='''periodicity, e.g. monthly, daily, etc. Default=monthly''',
                    default="monthly")
parser.add_argument("-a", "--start_date", dest="start_date",
                    help='''Start date in ISO format. Default=1-1-1''',
                    default='2001-1-1')
parser.add_argument("-e", "--end_date", dest="end_date",
                    help='''End date in ISO format. Default=4-1-1''',
                    default='2002-1-1')
parser.add_argument("-u", "--ref_unit", dest="ref_unit",
                    help='''Reference unit. Default=days. Use of months or
                    years is NOT recommended.''', default='days')
parser.add_argument("-d", "--ref_date", dest="ref_date",
                    help='''Reference date. Default=1-1-1''',
                    default='2001-1-1')

options = parser.parse_args()
periodicity = options.periodicity.upper()
start_date = parse(options.start_date)
end_date = parse(options.end_date)
ref_unit = options.ref_unit
ref_date = options.ref_date
args = options.FILE
infile = args[0]

# Check if file exists. If True, append, otherwise create it.
if os.path.isfile(infile):
    nc = NC(infile, 'a')
else:
    nc = NC(infile, 'w', format='NETCDF3_CLASSIC')


time_dim = 'time'
# create a new dimension for bounds only if it does not yet exist
bnds_dim = 'bnds'
if bnds_dim not in nc.dimensions.keys():
    nc.createDimension(bnds_dim, 2)

# variable names consistent with PISM
time_var_name = "time"
bnds_var_name = "time_bnds"

time_var = nc.variables[time_var_name]
time_var.units = 'days'
time_var.bounds = bnds_var_name
time_var.calendar = '365_day'

# create time bounds variable
time_bnds_var = nc.createVariable(bnds_var_name, 'd', dimensions=(time_dim, bnds_dim))
bnds = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
time_bnds_var[:, 0] = bnds[0:-1]
time_bnds_var[:, 1] = bnds[1::]

# writing global attributes
script_command = ' '.join([time.ctime(), ':', __file__.split('/')[-1],
                           ' '.join([str(x) for x in args])])
nc.history = script_command
nc.Conventions = "CF 1.5"
nc.close()
