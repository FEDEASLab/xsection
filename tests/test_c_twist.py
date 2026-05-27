from xsection._benchmarks import load_shape
from xsection.analysis import SaintVenantSectionAnalysis
import pytest 


def test_c01_material():
    E = 1e3
    material = {"E": E, "G": E/(2*(1+0.3))}
    shape = load_shape("C01", material=material)
    shape = shape.translate(-shape.centroid)
    sv = SaintVenantSectionAnalysis(shape)
    A = sv._A
    J = sv.twist_rigidity()/material["G"]


    assert A   == pytest.approx(    58.8, rel=0.1)
    assert J   == pytest.approx(      35, abs=1.0)
    # sy, sz = sv.twist_center()
    # assert sy  == pytest.approx( -6.0779, abs=0.06)
    # assert sz  == pytest.approx(     0.0, abs=5e-5)

    sy, sz = shape._analysis.shear_center()
    assert sy  == pytest.approx( -6.0779, abs=0.06)
    assert sz  == pytest.approx(     0.0, abs=5e-5)

def _test_c01_centroid():
    shape = load_shape("C01", nu=0.3)
    shape = shape.translate(-shape.centroid)
    sv = SaintVenantSectionAnalysis(shape)
    A   = shape.elastic.A
    Iy  = shape.elastic.Iy
    Iz  = shape.elastic.Iz
    Iyz = shape.elastic.Iyz
    J   = sv.twist_rigidity()/shape.material["G"]


    assert A   == pytest.approx(    58.8, rel=0.1)
    assert Iy  == pytest.approx(    8039, rel=0.1)
    assert Iz  == pytest.approx(     564, abs=0.3)
    assert Iyz == pytest.approx(     0.0, abs=1e-8)
    assert J   == pytest.approx(      35, abs=1.0)
    sy, sz = shape._analysis.shear_center()
    assert sy  == pytest.approx( -6.0779, abs=0.06)
    assert sz  == pytest.approx(     0.0, abs=5e-5)


def test_c04():
    # Pilkey
    E = 10
    material = {"E": E, "G": E/(2*(1+0.3))}
    shape = load_shape("C04", material=material, mesh_scale=1/25)
    shape = shape.translate(-shape.centroid)

    sv = SaintVenantSectionAnalysis(shape)

    J = sv.twist_rigidity()/material["G"]

    assert J == pytest.approx(  0.00133, rel=5e-2)

    sy, sz = shape._analysis.shear_center()
    assert sy == pytest.approx(-0.62056, rel=1e-1)
    assert sz == pytest.approx(0, abs=1e-5)

    tr = sv.create_trace(form="energetic")
    ky, kz = tr.sce()

    assert ky == pytest.approx(1/3.09621, rel=5e-2)
    assert kz == pytest.approx(1/2.34102, rel=5e-2)
