import pytest
from xara import Material

from xsection.analysis import SaintVenantSectionAnalysis
from xsection.library import Rectangle, Channel, HollowRectangle
from xsection._benchmarks import load_shape


MESH_TYPE = "T6"

# From Armero's full report, Table 1 on page 87
rectangle = [
#    t/h                     J             Jw        Jv               Js
    [1.0,  0,          2.25416620e4, 8.66423278e3,  4.12500467e3, 2.94805924e4],
    [0.5,  0,          4.58455629e3, 2.03297383e4,  3.74877704e3, 1.58209907e5],
    [0.1,  0,          5.02809625e1, 4.25107929e2,  1.29638570e3, 1.67786200e2]
]

channel = [
#    t/h      xsc           J             Jw
    [0.10, 2.28811887, 8.50099503e+1, 1.87665937e4, 4.44404677e3, 1.75869485e5],
#   [0.05, 2.59689539, 3.19982170e-1, 4.42779462e3, 9.28004807e2, 5.68392233e4],
    [0.01, 2.78436565, 9.53031691e-2, 3.03596030e3, 6.29488297e2, 3.96167673e4]
]

neuber = [
    [0.10,  1,         1.23677966e4,  1.57591655e3, 3.37620344e3,  3.81971644e3],
    [0.05,  1,         7.04796191e3,  2.82805259e2, 2.12270476e3,  7.18179690e2],
    # [0.01,  1,         1.56287589e3,  3.84789924e0, 5.07306512e2,  1.40319061e1],

    [0.10,  2,         1.50314876e4,  2.92100250e4, 5.23517907e3,  7.42990212e5],
    [0.05,  2,         8.96257119e3,  2.62850975e4, 3.78409548e3,  8.81626379e5],
    # [0.01,  2,         2.06474176e3,  8.03505311e3, 9.94116910e2,  3.12143230e5]
]

def _ShapeM01():
    # Section 7.5 of Armero's report

    from xsection.library import DoubleFlange, Rectangle
    from xsection import CompositeSection
    from xara import Section, Material 
    G = 76.92
    E = 200.0

    materials = {
        "1": Material(E=E, G=G),
        "2": Material(E=E/10, G=G/10)
    }

    h = 50
    t = 0.04*h
    bot = DoubleFlange(d=h,
                       b2=0.3*h, 
                       b1=0.6*h, 
                       t2=1.25*t,
                       t1=t, 
                       tw=t,
                       group="1", 
                       material=materials["1"],
                       mesh_scale=1/30
    )

    d = 0.2*h
    top = Rectangle(d=d, b=h, group="2", mesh_scale=1/40, material=materials["2"])
    top = top.translate([0, d/2+t/2])

    return CompositeSection([top, bot])


def test_composite():
    E1 = 200.0
    G1 = 76.92
    shape = load_shape("M01")
    # shape = ShapeM01()
    sv = SaintVenantSectionAnalysis(shape, nu=shape.materials["1"].nu)
    GJ = sv.twist_rigidity()
    J = GJ/G1
    Jw = shape.cww()[0,0]/E1
    Jv = shape.cvv()[0,0]/G1 
    Ja = sv.css()/E1

    assert J  == pytest.approx(4000, rel=1e-1) # 4.23488407e3
    assert Jv == pytest.approx(1.63767657e5, rel=2e-1)
    assert Jw == pytest.approx(1.75506164e6, rel=2e-1)
    assert Ja == pytest.approx(4.53999995e7, rel=2e-2)



def test_rectangle_T6():
    material = Material(E=1, G=1)

    for tr, _, J, Jw, Jv, Ja in rectangle:
        s = Rectangle(d=20,
                      b=tr*20, 
                      mesh_scale=1/15,
                      material=material,
                      mesher="gmsh",
                      mesh_type="T6")
        sv = SaintVenantSectionAnalysis(s)
        Jsc = sv.twist_rigidity()/material["G"]
        Jwc = s.cww()[0,0]/material["E"]
        Jvc = s.cvv()[0,0]/material["G"]
        Jac = s.css()

        assert Jsc == pytest.approx(J,  rel=1e-2)
        assert Jwc == pytest.approx(Jw, rel=1e-2)
        assert Jvc == pytest.approx(Jv, rel=2e-2)
        assert Jac == pytest.approx(Ja, rel=2e-2)


def test_rectangle_T3():
    for tr, _, J, Jw, Jv, Ja in rectangle:
        s = Rectangle(d=20,
                      b=tr*20, 
                      mesh_scale=1/60,
                      mesher="triangle",
                      mesh_type="T3")
        sv = SaintVenantSectionAnalysis(s)
        Jsc = sv.twist_rigidity()# s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = sv.css()

        assert Jsc == pytest.approx(J,  rel=1e-2)
        assert Jwc == pytest.approx(Jw, rel=1e-2)
        assert Jvc == pytest.approx(Jv, rel=1e-2)
        assert Jac == pytest.approx(Ja, rel=1e-2)


def test_rectangle_T3_material():
    material = Material(E=2, G=1)
    for tr, _, J, Jw, Jv, Ja in rectangle:
        s = Rectangle(d=20,
                      b=tr*20, 
                      material=material,
                      mesh_scale=1/60,
                      mesher="triangle",
                      mesh_type="T3")
        sv = SaintVenantSectionAnalysis(s)
        Jsc = sv.twist_rigidity()# s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]/material["E"]
        Jvc = s.cvv()[0,0]/material["G"]
        Jac = sv.css()/material["E"]

        assert Jsc == pytest.approx(J,  rel=1e-2)
        assert Jwc == pytest.approx(Jw, rel=1e-2)
        assert Jvc == pytest.approx(Jv, rel=1e-2)
        assert Jac == pytest.approx(Ja, rel=1e-2), float(Jac/Ja)



def test_channel():
    #
    # Channel
    #
    for tr, xsc, J, Jw, Jv, Ja, in channel:
        print(f"Channel<t/h={tr}>")
        s = Channel(
                d=20,
                b=0.4*20,
                tf=tr*20,
                tw=tr*20,
                mesh_scale=1/5, # 30
                mesh_type="T6",
                mesher="gmsh"
        )

        sv = SaintVenantSectionAnalysis(s)
        s = s.translate(-s._analysis.shear_center())
        Jsc = sv.twist_rigidity()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = s.css()
        assert Jsc == pytest.approx(J,  rel=1e-2)
        assert Jwc == pytest.approx(Jw, rel=1e-2)
        assert Jvc == pytest.approx(Jv, rel=1e-2)
        assert Jac == pytest.approx(Ja, rel=1e-2)


def test_neuber_T6_triangle():
    for tr, rwf, J, Jw, Jv, Ja in neuber:
        tw = 20*tr
        tf = rwf*tw
        s = HollowRectangle(
                d=20,
                b=20,
                tw=tw,
                tf=tf,
                mesh_scale=1/30,
                mesh_type="T6"
        )

        Jsc = s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = s.css()
        # print("J   {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jsc         -J )/J , Jsc, J ))
        # print("Jw  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cww()[0,0]-Jw)/Jw, Jwc, Jw))
        # print("Jv  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cvv()[0,0]-Jv)/Jv, Jvc, Jv))
        # print("Ja  {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jac         -Ja)/Ja, Jac, Ja))
        # print()
        assert Jsc == pytest.approx(J,  rel=1e-2)
        assert Jwc == pytest.approx(Jw, rel=1e-1)
        assert Jvc == pytest.approx(Jv, rel=1e-2)
        assert Jac == pytest.approx(Ja, rel=2e-1)


if __name__ == "__main__":


    HEADER = "      Error        Value       Reference"

    for tr, _, J, Jw, Jv, Ja in rectangle:
        s = Rectangle(d=20, 
                      b=tr*20, 
                      mesh_scale=1/10,
                      mesher="gmsh",
                      mesh_type=MESH_TYPE)
        Jsc = s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = s.css()

        print(HEADER)
        print("J   {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jsc         -J )/J , Jsc, J ))
        print("Jw  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cww()[0,0]-Jw)/Jw, Jwc, Jw))
        print("Jv  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cvv()[0,0]-Jv)/Jv, Jvc, Jv))
        print("Ja  {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jac         -Ja)/Ja, Jac, Ja))
        print()

#       print(s.summary())

    #
    # Channel
    #

    for tr, xsc, J, Jw, Jv, Ja, in channel:
        print(f"Channel<t/h={tr}>")
        s = Channel(
                d=20,
                b=0.4*20,
                tf=tr*20,
                tw=tr*20,
                mesh_scale=1/80, mesh_type=MESH_TYPE)
        s = s.translate(-s._analysis.shear_center())
        Jsc = s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = s.css()
        print(HEADER)
        print("J   {:>8.4f}  {:>10.3f} {:>10.3f}".format((Jsc         -J )/J , Jsc, J ))
        print("Jw  {:>8.4f}  {:>10.3f} {:>10.3f}".format((s.cww()[0,0]-Jw)/Jw, Jwc, Jw))
        print("Jv  {:>8.4f}  {:>10.3f} {:>10.3f}".format((s.cvv()[0,0]-Jv)/Jv, Jvc, Jv))
        print("Ja  {:>8.4f}  {:>10.3f} {:>10.3f}".format((Jac         -Ja)/Ja, Jac, Ja))
        print()

    for tr, rwf, J, Jw, Jv, Ja in neuber:
        tw = 20*tr
        tf = rwf*tw
        s = HollowRectangle(
                d=20,
                b=20,
                tw=tw,
                tf=tf,
                mesh_scale=1/60, 
                mesh_type=MESH_TYPE)
        Jsc = s._analysis.torsion_constant()
        Jwc = s.cww()[0,0]
        Jvc = s.cvv()[0,0]
        Jac = s.css()
        print(HEADER)
        print("J   {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jsc         -J )/J , Jsc, J ))
        print("Jw  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cww()[0,0]-Jw)/Jw, Jwc, Jw))
        print("Jv  {:8.4f}\t {:8.4f}\t {:8.4f}".format((s.cvv()[0,0]-Jv)/Jv, Jvc, Jv))
        print("Ja  {:8.4f}\t {:8.4f}\t {:8.4f}".format((Jac         -Ja)/Ja, Jac, Ja))
        print()

