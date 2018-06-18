# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2018)
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

"""Unit tests for :mod:`gwpy.plot`
"""

import os.path
import tempfile

from six.moves import StringIO

import pytest

import numpy

from matplotlib import (pyplot, rc_context)

from astropy.units import Unit

from ...segments import (Segment, SegmentList)
from ...tests import utils
from ...types import (Series, Array2D)
from .. import (Plot, Axes, BodePlot)
from .utils import (usetex, FigureTestBase)

numpy.random.seed(0)


# -- test classes -------------------------------------------------------------

class TestPlot(FigureTestBase):
    FIGURE_CLASS = Plot

    def test_init(self):
        plot = self.FIGURE_CLASS(figsize=(4, 3), dpi=100)
        assert tuple(plot.get_size_inches()) == (4., 3.)
        assert plot.colorbars == []

    def test_init_with_data(self):
        a = Series(range(10), dx=.1)
        plot = self.FIGURE_CLASS(a)
        assert len(plot.axes) == 1

        ax = plot.gca()
        assert len(ax.lines) == 1

        line = ax.lines[0]
        utils.assert_quantity_equal(line.get_xdata(), a.xindex)
        utils.assert_quantity_equal(line.get_ydata(), a)

        plot.close()

        # ----

        b = Series(range(10), dx=.1)

        plot = self.FIGURE_CLASS(a, b)
        assert len(plot.axes) == 1
        assert len(plot.axes[0].lines) == 2
        plot.close()

        plot = self.FIGURE_CLASS(a, b, separate=True, sharex=True, sharey=True)
        assert len(plot.axes) == 2
        for i, ax in enumerate(plot.axes):
            assert ax.get_geometry() == (2, 1, i+1)
            assert len(ax.lines) == 1
        assert plot.axes[1]._sharex is plot.axes[0]
        plot.close()

        array = Array2D(numpy.random.random((10, 10)), dx=.1, dy=.2)
        plot = self.FIGURE_CLASS(array, method='imshow')
        assert len(plot.axes[0].images) == 1
        image = plot.axes[0].images[0]
        utils.assert_array_equal(image.get_array(), array.value.T)
        plot.close()

    def test_save(self, fig):
        with tempfile.NamedTemporaryFile(suffix='.png') as f:
            fig.save(f.name)
            assert os.path.isfile(f.name)

    def test_get_axes(self, fig):
        fig.add_subplot(2, 1, 1, projection='rectilinear')
        fig.add_subplot(2, 1, 2, projection='polar')
        assert fig.get_axes() == fig.axes
        assert fig.get_axes(projection='polar') == fig.axes[1:]

    def test_colorbar(self, fig):
        ax = fig.gca()
        array = Array2D(numpy.random.random((10, 10)), dx=.1, dy=.2)
        image = ax.imshow(array)
        cbar = fig.colorbar(vmin=2, vmax=4, fraction=0.)
        assert cbar.mappable is image
        assert cbar.get_clim() == (2., 4.)

    def test_add_colorbar(self, fig):
        ax = fig.gca()
        array = Array2D(numpy.random.random((10, 10)), dx=.1, dy=.2)
        image = ax.imshow(array)
        with pytest.warns(DeprecationWarning):
            cbar = fig.add_colorbar(vmin=2, vmax=4, fraction=0.)
        assert cbar.mappable is image

    def test_add_segments_bar(self, fig):
        ax = fig.gca(xscale='auto-gps')
        ax.set_xlim(100, 200)
        ax.set_xlabel('test')
        segs = SegmentList([Segment(10, 110), Segment(150, 400)])
        segax = fig.add_segments_bar(segs)
        assert segax._sharex is ax
        assert ax.get_xlabel() == ''

        # check that it works again
        segax = fig.add_segments_bar(segs, ax=ax)

        # check errors
        with pytest.raises(ValueError):
            fig.add_segments_bar(segs, location='left')

    def test_add_state_segments(self, fig):
        ax = fig.gca(xscale='auto-gps')
        segs = SegmentList([Segment(10, 110), Segment(150, 400)])
        with pytest.warns(DeprecationWarning):
            fig.add_state_segments(segs)