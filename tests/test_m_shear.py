from math import pi
import pytest
from xsection import CompositeSection
from xsection.library import Rectangle
from xsection.properties import torsion_constant
from xsection.analysis.venant import SaintVenantSectionAnalysis


def test_shape():
    """
    El Fatmi, Rached, and Hatem Zenzri. 
      "A Numerical Method for the Exact Elastic Beam Theory. Applications to Homogeneous and Composite Beams." 
      International Journal of Solids and Structures 41, nos. 9–10 (2004): 2521–37. 
      https://doi.org/10.1016/j.ijsolstr.2003.12.011.
    """
    materials = {
        "1": {"E": 72.95e3, "G": 27.51e3},
        "2": {"E": 10.67e3, "G":  4.02e3}
    }
    s1 = Rectangle(d=40, b=30, material=materials["1"], group="1", mesh_scale=1/30, z=1)
    s2 = Rectangle(d=35, b=20, material=materials["2"], group="2", mesh_scale=1/20, z=2)
    s2 = s2.translate([0, 2.5])
    # s2 = Channel(d=30, b=40, t=5, material=materials["2"], group="2", mesh_scale=1/10, z=1)
    # s2 = s2.translate([-15, 0]).rotate(pi/2)#.translate([0, -15])
    shape = CompositeSection([s1,s2])


    shape = shape.translate(-shape._analysis.centroid())

    sv1 = SaintVenantSectionAnalysis(s1, nu=0.33)

    print(torsion_constant(s1))
    print(sv1.twist_rigidity()/s1.material["G"])


    sv = SaintVenantSectionAnalysis(shape, nu=0.33)
    assert sv.twist_rigidity()/sv1.twist_rigidity() == pytest.approx(0.525, rel=1e-3)

    tr = sv.create_trace(form="energetic")
    ky, kz = tr.sce()

    assert ky == pytest.approx(0.428, rel=5e-3)
    assert kz == pytest.approx(0.727, rel=5e-3)

    # return s1, shape


if __name__ == "__main__":
    import veux 
    s1, shape = test_shape()

    artist = veux.render(shape.model)
    veux.serve(artist)
