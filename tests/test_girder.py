
import pytest
from xsection.library._asbi import create_asbi, SingleCellGirder
from xsection.analysis import SaintVenantSectionAnalysis
from xsection._benchmarks import load_shape
r"""
2400-2:
    \begin{tabular}{|l|l|l|l|l|l|}
    \hline Deck Width (mm) & 'A' (mm) & Area (mm²) & $\mathrm{Wt} / 3,000 \mathrm{~mm}$ (Kn) & lx ( $\mathrm{m}^4$ ) & Yt (mm) \\
    10,800 & 0 & 6.327,000 & 463 & 5.045 & 882 \\
    11,100 & 150 & 6,395,000 & 468 & 5.085 & 874 \\
    11,400 & 300 & 6,462,000 & 473 & 5.124 & 866 \\
    11,700 & 450 & 6,530,000 & 478 & 5.162 & 858 \\
    12,000 & 600 & 6,597,000 & 483 & 5.199 & 851 \\
    12,300 & 750 & 6,665,000 & 488 & 5.236 & 843 \\
    12,600 & 900 & 6,732,000 & 493 & 5.272 & 836 \\
    12,900 & 1,050 & 6,800,000 & 498 & 5.307 & 829 \\
    13,200 & 1,200 & 6,867,000 & 503 & 5.342 & 821 \\
    13,500 & 1,350 & 6,935,000 & 508 & 5.376 & 815 \\
    \hline
    \end{tabular}

2700-1:
    \begin{tabular}{|l|l|l|l|l|l|}
    \hline Deck Width (mm) & 'A' (mm) & Area (mm²) & $\mathrm{Wt} / 3,000 \mathrm{~mm}$ (Kn) & Ix (m^) & Yt (mm) \\
    8,400 & 0 & 5,471,000 & 401 & 5.368 & 1,021 \\
    8,700 & 150 & 5,539,000 & 405 & 5.423 & 1,010 \\
    9,000 & 300 & 5,606,000 & 410 & 5.477 & 999 \\
    9,300 & 450 & 5,674,000 & 415 & 5.530 & 989 \\
    9,600 & 600 & 5,741,000 & 420 & 5.581 & 978 \\
    9,900 & 750 & 5,809,000 & 425 & 5.632 & 968 \\
    10,200 & 900 & 5,876,000 & 430 & 5.681 & 958 \\
    10,500 & 1,050 & 5,944,000 & 435 & 5.729 & 949 \\
    10,800 & 1,200 & 6,011,000 & 440 & 5.776 & 939 \\
    11,100 & 1,350 & 6,079,000 & 445 & 5.822 & 930 \\
    11,400 & 1,500 & 6,146,000 & 450 & 5.867 & 921 \\
    \hline
    \end{tabular}
"""


def test_asbi():

    # Flat soffit
    shape = create_asbi("SS-1800-1", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(3_920_000*u.mm**2, rel=2e-2)

    shape = create_asbi("SS-1800-1+150", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(3_988_000*u.mm**2, rel=2e-2)

    shape = create_asbi("SS-1800-2+150", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(5_032_000*u.mm**2, rel=2e-2)


    # Raised soffit
    shape = create_asbi("BC-1800-1", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(4_687_000*u.mm**2, rel=1e-2)

    shape = create_asbi("BC-1800-2", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(5_805_000*u.mm**2, rel=1e-2)


    shape = create_asbi("BC-2100-1", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(4_916_000*u.mm**2, rel=1e-2)

    shape = create_asbi("BC-2100-1+900", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(5_321_000*u.mm**2, rel=1e-2)

    shape = create_asbi("BC-2100-1+1500", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(5_591_000*u.mm**2, rel=1e-2)

    shape = create_asbi("BC-2700-1", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(5_471_000*u.mm**2, rel=1e-2)

    shape = create_asbi("BC-3000-1+750", mesher="gmsh")
    u = shape.units
    assert shape.area == pytest.approx(6_135_000*u.mm**2, rel=1e-2)



def test_torsion():

    shape = load_shape("G02", mesh_type="T6", mesh_scale=1)

    sv = SaintVenantSectionAnalysis(shape)
    assert sv.twist_rigidity()/shape.material["G"] == pytest.approx(42.487, rel=1e-1)

    # shape = shape.translate(-sv.twist_center())
    # assert shape.cww()[0,0]/shape.material["E"] == pytest.approx(62.788, rel=2e-1)

    tr = sv.create_trace(form="energetic")
    ky, kz = tr.sce()
    assert ky == pytest.approx(0.5993, rel=1e-3)
    assert kz == pytest.approx(0.2311, rel=1e-2)



def test_fhwa():
    # Example 1, page 271/369
    #  https://www.fhwa.dot.gov/bridge/concrete/hif15016.pdf

    material = {"E": 4, "G": 2}
    shape = load_shape("G03", material=material, mesh_type="T6", mesh_scale=1/3)
    u = shape.units

    sv = SaintVenantSectionAnalysis(shape)
    J = sv.twist_rigidity()/shape.material["G"]

    assert J == pytest.approx(1697.5*u.ft**4, rel=5e-2)
