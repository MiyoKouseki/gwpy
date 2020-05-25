# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2013)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Read a `Series` from  GIF file

These files should be in gif data style
"""

from numpy import (column_stack, fromfile, arange, isclose, diff)
from scipy.signal import decimate
#from miyopy.gif import fname2gps
import numpy as np

from ...io import registry as io_registry
from ...io.utils import identify_factory
from .. import Series
from miyopy.gif import GifData
__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

# --
from astropy.time import Time
from datetime import datetime,timedelta
def fname2gps(fname):
    '''
    '''
    datetime_str = fname.split('.')[0].split('/')[-1]
    time = datetime.strptime(datetime_str, '%y%m%d%H%M') # JST
    time = time - timedelta(hours=9) # JST -> UTC
    gps = Time(time,scale='utc').gps # UTC->GPS
    return gps

# def gps2datestr(gps):
#     utc = Time(gps, format='gps').to_datetime()
#     date_str = utc.strftime('%Y%m%d%H%M')
#     return date_str

# -- read ---------------------------------------------------------------------

def read_gif_series(input_, array_type=Series, **kwargs):
    """Read a `Series` from an GIF file

    Parameters
    ----------
    input_ : `str`, `file`
        single input file
    
    array_type : `type`, optional
        desired return type
    
    """
    chname = kwargs.pop('name',None)
    yarr = GifData.fromfile(input_, chname)
    fs = GifData(chname).fs
    x0 = fname2gps(input_)
    arr = array_type(yarr,  x0=x0, dx=1./fs, name=chname)
    return arr

# -- write --------------------------------------------------------------------

def write_gif_series(series, output, **kwargs):
    """Write a `Series` to a file in GIF format

    Parameters
    ----------
    series : :class:`~gwpy.data.Series`
        data series to write

    output : `str`, `file`
        file to write to
        
    See also
    --------
    numpy.savetxt
        for documentation of keyword arguments
    """
    #xarr = series.xindex.value
    #yarr = series.value
    #return savetxt(output, column_stack((xarr, yarr)), **kwargs)


# -- register -----------------------------------------------------------------

def register_gif_series_io(array_type, format='gif', identify=True,
                             **defaults):
    """Register GIF read/write/identify methods for the given array
    """
    def _read(filepath, **kwargs):
        kwgs = defaults.copy()
        kwgs.update(kwargs)
        return read_gif_series(filepath, array_type=array_type, **kwgs)

    def _write(series, output, **kwargs):
        kwgs = defaults.copy()
        kwgs.update(kwargs)
        return write_gif_series(series, output, **kwgs)
    
    io_registry.register_reader(format, array_type, _read)
    io_registry.register_writer(format, array_type, _write)
    if identify:
        io_registry.register_identifier(format, array_type,
                                        identify_factory(format))
