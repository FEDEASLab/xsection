
import pytest
from xsection.library import load_shape

def test_aisc_angle():
    shape = load_shape("L7x4x3/4", 
                       library="AISC16",
                       mesh_scale=1/4, 
                       mesher="gmsh",
                       mesh_type="T6")
    
    assert shape.area  == pytest.approx(7.74, rel=1e-2)
