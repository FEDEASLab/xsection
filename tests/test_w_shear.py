import pytest
from xsection.library import WideFlange, from_aisc
from xsection.analysis import SaintVenantSectionAnalysis
import numpy as np

point_poisson = [#-0.9, -0.5, 
                 0, 0.3, 0.499]

def wide_flange_cowper(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d

    m = 2*b*tf/(d*tw)
    n = b/d

    D = ((12 + 72*m + 150*m**2 + 90*m**3) + nu*(11+66*m + 135*m**2 + 90*m**3) + 30*n**2*(m + m**2) + 5*nu*n**2*(8*m+9*m**2))
    return (10*(1+nu)*(1+3*m)**2)/D


def single_flange_cowper(shape: WideFlange, nu):
    r"""
    $\frac{10(1+\nu)(1+4 m)^2}{\left(12+96 m+276 m^2+192 m^3\right)+\nu\left(11+88 m+248 m^2+216 m^3\right)+30 n^2\left(m+m^2\right)+10 \nu n^2\left(4 m+5 m^2+m^3\right)}$
    """
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d

    m = b*tf/(d*tw)
    n = b/d
    D = (12 + 96*m + 276*m**2 + 192*m**3) + nu*(11 + 88*m + 248*m**2 + 216*m**3) + 30*n**2*(m+m**2) + 10*nu*n**2*(4*m+5*m**2+m**3)
    return (10*(1+nu)*(1+4*m)**2)/D


def wide_flange_timoshenko(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d
    A  = shape.area
    I  = shape.elastic.Iy
    return float(8*tw*I/(A*(b*d**2 - (b - tw)*(d - 2*tf)**2)))


def wide_flange_newlin(shape: WideFlange, nu=0.3):
    b  = shape.bf
    tf = shape.tf
    tw = shape.tw
    d  = shape.d
    A  = shape.area
    I  = shape.elastic.Iy
    d1 = d - 2*tf
    aw = A*b/(64*I**2)*(d1**5*(8*tw/(15*b)+b/tw-4/3)-d1**3*d**2*(2*b/tw-4/3)+d1*d**4*(b/tw))
    af = A*b/(64*I**2)*(-d1**5/5 + 2/3*d1**3*d**2 - d1*d**4 + 8/15*d**5)
    return float(1/(aw + af))




def test_poisson():
    for name in [ "W14x48"]: # "W18x40",
        shape = from_aisc(name, mesh_scale=1/10, fillet=False, mesher="gmsh", mesh_type="T6")
        for nu in [0, 0.3]:
            sv = SaintVenantSectionAnalysis(shape, nu=nu)
            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] > 0
            assert cowper[1] == pytest.approx(wide_flange_cowper(shape, nu=nu), rel=1e-2)



def test_single_flange():
    for name in ["WT18x115.5"]:
        shape = from_aisc(name, mesh_scale=1/10, fillet=False, mesher="gmsh", mesh_type="T6")
        shape = shape.translate(-shape.centroid)
        for nu in [0, 0.3]:
            sv = SaintVenantSectionAnalysis(shape, nu=nu)
            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] > 0
            assert cowper[1] == pytest.approx(single_flange_cowper(shape, nu=nu), rel=5e-2)




# def test_material():
#     for name in ["W18x40"]:
#         shape = from_aisc(name, mesh_scale=1/10, fillet=False, mesher="gmsh", mesh_type="T6")
#         for nu in [0, 0.3]:
#             sv = SaintVenantSectionAnalysis(shape, nu=nu)
#             cowper = sv.create_trace(form="geometric").sce()
#             assert cowper[0] > 0
#             assert cowper[1] == pytest.approx(wide_flange_cowper(shape, nu=nu), rel=1e-2)



if __name__ == "__main__":
    import sys
    # "W14x48"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "W18x40"

    print("Section:", name)

    shape = from_aisc(name, mesh_scale=1/10, fillet=False, mesher="gmsh")

    print("A/(d*tw)",     shape.depth*shape.tw/shape.elastic.A)
    for nu in 0.3, 0:
        print(f"nu = {nu}")
        print(" Cowper\t\t",     wide_flange_cowper(shape, nu=nu))
        print(" Timoshenko\t",   wide_flange_timoshenko(shape, nu=nu))
        print(" Newlin\t\t",     wide_flange_newlin(shape, nu=nu))

        shear_model = shape._analysis.shear_model(nu=nu)
        Xr = shape._analysis.shear_factor_romano(nu=0.0)[0][1]
        print(" Romano\t\t", Xr)
        print(" Cowper\t\t", shear_model.correction(form="average"))
        print("-"*10, "\n")

