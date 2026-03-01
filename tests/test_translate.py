import pytest
import numpy as np
from tests.shapes import create_section
from xsection._benchmarks import load_shape
from xsection.library import from_aisc, Rectangle, HollowRectangle, Channel, WideFlange

def shift_inertia(r, centroid, A):
    I = np.eye(2)
    return 2*A*np.dot(r, centroid)*I \
        - A*(np.outer(r, centroid) + np.outer(centroid, r)) \
        + A*(np.dot(r, r)*I - np.outer(r, r))

def _check_translate(shape, r):
    shape_t = shape.translate(r)

    A    = shape.geometric.A
    Iy0  = shape.geometric.Iy
    Iz0  = shape.geometric.Iz
    Iyz0 = shape.geometric.Iyz

    Iy1  = shape_t.geometric.Iy
    Iz1  = shape_t.geometric.Iz
    Iyz1 = shape_t.geometric.Iyz

    dI = shift_inertia(r, shape.centroid, A)
    dIy = dI[0,0]
    dIz = dI[1,1]
    assert Iy1 == pytest.approx(Iy0 + dIy, abs=1e-8)
    assert Iz1 == pytest.approx(Iz0 + dIz, abs=1e-8)
    # assert Iyz1 == pytest.approx(Iyz0 + A*r[0]*r[1], abs=1e-8)


def test_translate_rect():
    _check_translate(load_shape("R01"), (3.0, 4.0))

def test_translate_hrect():
    _check_translate(load_shape("H07"), (3.0, 4.0))
    _check_translate(load_shape("H08"), (3.0, 4.0))


def test_translate_channel():
    _check_translate(load_shape("C10"), (3.0, 4.0))


def test_girder():
    _check_translate(load_shape("G03"), (3.0, 4.0))

def _test_composite():
    shape = load_shape("M01")
    _check_translate(shape, (3.0, 4.0))