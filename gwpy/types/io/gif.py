
"""Read a `Series` from AN GIF file

These files should be in two-column x,y format
"""

from numpy import (savetxt, loadtxt, column_stack, fromfile, arange)

from ...io import registry as io_registry
from ...io.utils import identify_factory
from .. import Series

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"


# -- read ---------------------------------------------------------------------

def read_gif_series(input_, array_type=Series, unpack=True, **kwargs):
    """Read a `Series` from an GIF file

    Parameters
    ----------
    input : `str`, `file`
        file to read

    array_type : `type`
        desired return type
    """
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)
    tlen = end - start
    fs = 200.0
    #
    yarr = fromfile(input_)        
    xarr = arange(len(yarr))/fs # suport only strain data of 200 Hz
    xarr = xarr + start
    return array_type(yarr, xindex=xarr, dx=1./fs, unit='strain')


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
    return savetxt(output, column_stack((xarr, yarr)), **kwargs)


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
