import sys
import pytest
import veux
import numpy as np
from xara.units import us, si
from xsection.library import from_aisc, aisc_data


def _check_data(shape, data):
    assert shape.A  == pytest.approx(data["A"],  abs=0.5)
    assert shape.Iy == pytest.approx(data["Ix"], rel=1e-2)
    assert shape.Iz == pytest.approx(data["Iy"], rel=1e-2)
    assert shape.Iyz == pytest.approx(0.0, abs=1e-8)


def test_units_():
    shape_us = from_aisc("W14x48", units=us).elastic
    shape_si = from_aisc("W14x48", units=si).elastic

    L = getattr(us, si.Length)

    assert shape_us.A  == pytest.approx(shape_si.A*L**2,  rel=1e-8)
    assert shape_us.Iy == pytest.approx(shape_si.Iy*L**4, rel=1e-8)
    assert shape_us.Iz == pytest.approx(shape_si.Iz*L**4, rel=1e-8)


def test_data_w():
    data = aisc_data("W14x48")
    shape = from_aisc("W14x48", mesh_scale=1/5).elastic
    _check_data(shape, data)


def test_data_wt():
    data = aisc_data("WT22X145")
    shape = from_aisc("WT22X145", mesh_scale=1/5)
    shape = shape.translate(-shape.centroid).elastic
    _check_data(shape, data)


# def test_data_c():
#     data = aisc_data("C15x50")
#     shape = from_aisc("C15x50", mesh_scale=1/10, mesher="gmsh")
#     shape = shape.translate(-shape.centroid).elastic
#     assert shape.A  == pytest.approx(data["A"],  rel=0.35)
#     assert shape.Iy == pytest.approx(data["Ix"], rel=0.25)
#     assert shape.Iz == pytest.approx(data["Iy"], rel=0.25)
#     assert shape.Iyz == pytest.approx(0.0, abs=1e-8)


if __name__ == "__main__":
    from xsection.analysis.interaction import limit_surface, plot_limit_surface
    c = "centroid"

    shape = from_aisc(sys.argv[1], mesh_scale=1/20)
    d = shape.d

    if False:
        pass
    elif c == "shear-center":
        shape = shape.translate(-shape._analysis.shear_center())

    elif c == "centroid":
        print(f"{shape.centroid = }")
        shape = shape.translate(-shape.centroid)

    else:
        shape = shape.translate(c)

    print(shape.summary(shear=True))

    print("tan(alpha): ", np.tan(shape._principal_rotation()))

#   _test_opensees(shape,
#                  section=os.environ.get("Section", "fiber"),
#                  center =os.environ.get("Center", None)
#   )

    # 1) create basic section
#   basic = shape.linearize()

#   field = shape._analysis.warping()
    field = shape._analysis.fiber_shear()[1]

    # 3) view warping modes
    artist = veux.create_artist(shape.model, ndf=1, ndm=2)

    field = {node: (shape.depth/8)*value/max(field) for node, value in enumerate(field)}

    artist.draw_surfaces(field = field,
                         #state=field
                         )
    artist.draw_outlines()
    R = artist._plot_rotation

    artist.canvas.plot_vectors([[0,0,0] for i in range(3)], d/5*R.T, extrude=True)
    artist.canvas.plot_vectors([R@[*shape._analysis.shear_center(), 0] for i in range(3)], d/5*R.T, extrude=True)
    artist.draw_outlines()
    veux.serve(artist)
