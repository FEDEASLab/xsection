from xsection._benchmarks import load_shape
from xsection.analysis import SaintVenantSectionAnalysis
import pytest 





def test_r01_centroid():
    shape = load_shape("R01")
    shape = shape.translate(-shape.centroid)
    d  = shape.d
    b  = shape.b
    A  = shape.elastic.A
    Iy = shape.elastic.Iy
    Iz = shape.elastic.Iz
    Iyz = shape.elastic.Iyz

    assert A   == pytest.approx(      d*b, rel=1e-3)
    assert Iz  == pytest.approx(d*b**3/12, rel=1e-3)
    assert Iy  == pytest.approx(d**3*b/12, rel=1e-3)
    assert Iyz == pytest.approx(      0.0, abs=1e-8)



if __name__ == "__main__":
    import veux
    from veux.config import NodeStyle
    from xsection.library import Rectangle
    width  = 12
    depth  = 18

    Iy = width * depth**3 / 12
    Iz = depth * width**3 / 12
    print(f"Iy = {Iy}, Iz = {Iz}")

    shape = Rectangle(d=depth, b=width, mesh_scale=3)

    print(shape.summary())

    a = veux.render(shape.model)

    for fiber in shape.create_fibers():
        print(fiber)

    Rc = a._plot_rotation.T
    for fiber in shape.create_fibers():
        a.canvas.plot_nodes([Rc@[fiber["y"], fiber["z"], 0]], style=NodeStyle(color="blue", scale=1))

    veux.serve(a)
