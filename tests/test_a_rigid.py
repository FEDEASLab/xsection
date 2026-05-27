
import pytest
from xsection.library import load_shape
from xsection.analysis import SaintVenantSectionAnalysis

def test_aisc_angle():
    shape = load_shape("L7x4x3/4", 
                       library="AISC16",
                       mesh_scale=1/4, 
                       mesher="gmsh",
                       mesh_type="T6")
    
    assert shape.area  == pytest.approx(7.74, rel=1e-2)

def _test_aisc_angle_twist_center():
    shape = load_shape("L7x4x3/4", 
                       library="AISC16",
                       mesh_scale=1/8, 
                       mesher="gmsh",
                       fillet=False,
                       mesh_type="T6")
    # sv = SaintVenantSectionAnalysis(shape)
    # sy, sz = sv.twist_center()
    sy, sz = shape._analysis.shear_center()
    assert sy  == pytest.approx( 0, abs=0.1*shape.t)
    assert sz  == pytest.approx( 0, abs=0.1*shape.t)
