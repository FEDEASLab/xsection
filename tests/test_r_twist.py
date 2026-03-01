import pytest

from xsection.analysis.venant import SaintVenantSectionAnalysis 
from xsection.library import Rectangle
from xsection.properties import torsion_constant


def test_T3():

    shape = Rectangle(b=3, d=5, 
                      mesh_scale=1/40,
                      mesher="triangle",
                      mesh_type="T3")
    sv = SaintVenantSectionAnalysis(shape, nu=0.3)
    assert sv._A == pytest.approx(shape.d*shape.b, rel=1e-6)

    J = torsion_constant(shape)
    assert sv.twist_rigidity() == pytest.approx(J, rel=1e-2)


def test_T3_material():

    shape = Rectangle(b=3, d=5, 
                      mesh_scale=1/40,
                      material={"E": 4, "G": 2},
                      mesher="triangle",
                      mesh_type="T3")
    sv = SaintVenantSectionAnalysis(shape)
    assert sv._A == pytest.approx(shape.d*shape.b, rel=1e-6)
    assert sv._EA == pytest.approx(shape.d*shape.b*shape.material["E"], rel=1e-6)

    J = torsion_constant(shape)
    assert sv.twist_rigidity()/shape.material["G"] == pytest.approx(J, rel=1e-2)

    


def test_T6():
    shape = Rectangle(b=3, d=5, 
                      mesh_scale=1/5,
                      mesher="triangle",
                      mesh_type="T6")

    sv = SaintVenantSectionAnalysis(shape, nu=0.3)
    assert sv._A == pytest.approx(shape.d*shape.b, rel=1e-6)

    J = torsion_constant(shape)
    assert sv.torsion_constant() == pytest.approx(J, rel=1e-2)


    ic = sv.iesan_center()
    # print("Iesan center:", ic)
    assert ic[0] == pytest.approx(0, abs=1e-3)
    assert ic[1] == pytest.approx(0, abs=1e-3)



def test_T6_gmsh():
    from xsection.analysis.venant import SaintVenantSectionAnalysis 
    from xsection.library import Rectangle
    from xsection.properties import torsion_constant
    material = {"E": 4, "G": 2}
    shape = Rectangle(b=3, d=5,
                      mesh_scale=1/10,
                      material=material,
                      mesher="gmsh",
                      mesh_type="T6")
    sv = SaintVenantSectionAnalysis(shape)#, nu=0.3)
    assert sv._A == pytest.approx(shape.d*shape.b, rel=1e-6)

    J = torsion_constant(shape)
    assert sv.twist_rigidity()/material["G"] == pytest.approx(J, rel=1e-2)


    ic = sv.iesan_center()
    assert ic[0] == pytest.approx(0, abs=1e-3)
    assert ic[1] == pytest.approx(0, abs=1e-3)


def test_T6_material_gmsh():
    from xsection.analysis.venant import SaintVenantSectionAnalysis 
    from xsection.library import Rectangle
    from xsection.properties import torsion_constant

    shape = Rectangle(b=3, d=5,
                      mesh_scale=1/10,
                      material={"E": 4, "G": 2},
                      mesher="gmsh",
                      mesh_type="T6")
    sv = SaintVenantSectionAnalysis(shape, nu=0.3)
    assert sv._A == pytest.approx(shape.d*shape.b, rel=1e-6)
    assert sv._EA == pytest.approx(shape.d*shape.b*shape.material["E"], rel=1e-6)
    assert sv._GA == pytest.approx(shape.d*shape.b*shape.material["G"], rel=1e-6)

    J = torsion_constant(shape)
    assert sv.twist_rigidity()/shape.material["G"] == pytest.approx(J, rel=1e-2)


    ic = sv.iesan_center()
    assert ic[0] == pytest.approx(0, abs=1e-3)
    assert ic[1] == pytest.approx(0, abs=1e-3)
