"""gif I/O registrations for gwpy.timeseries objects
"""

from ...types.io.gif import register_gif_series_io
from .. import (TimeSeries, StateVector)

# -- registration -------------------------------------------------------------

register_gif_series_io(TimeSeries, format='gif')
#register_gif_series_io(TimeSeries, format='csv', delimiter=',')
register_gif_series_io(StateVector, format='gif')
#register_gif_series_io(StateVector, format='csv', delimiter=',')
