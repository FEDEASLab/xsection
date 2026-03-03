import pytest
from xsection.library import WideFlange
from xsection._benchmarks import load_shape, ShapeM03



d = 1
b = 1
tf = 0.1
tw = 0.1
A_ref = (d-2*tf)*tw + 2*tf*b


def test_1():

    for elem in ["T3", "T6"]:
        for mesher in ["triangle", "gmsh"]:
            shape = WideFlange(d=d, b=b, tf=tf, tw=tw, 
                mesh_scale=1, 
                mesher=mesher, 
                mesh_type=elem,
                group="1")
            A = 0
            for fiber in shape.create_fibers(group="1"):
                A += fiber["area"]
            assert A == pytest.approx(A_ref, rel=1e-8)


def test_2():
    """
    Test that the area of the fibers in a group is equal to the area of the shape.
    """
    for elem in ["T3", "T6"]:
        for mesher in ["triangle", "gmsh"]:
            shape = WideFlange(d=d, b=b, tf=tf, tw=tw, 
                mesh_scale=1, 
                mesher=mesher, 
                mesh_type=elem,
                group="1")
            A = 0
            for fiber in shape._create_fibers(shape.model, [], group="1"):
                A += fiber["area"]
            assert A == pytest.approx(A_ref, rel=1e-8)


def test_m01():
    shape = load_shape("M01")

    A1 = 0
    for fiber in shape.create_fibers(group="1"):
        A1 += fiber["area"]

    A2 = 0
    for fiber in shape.create_fibers(group="2"):
        A2 += fiber["area"]

    
    assert A2 == pytest.approx(shape._shapes[0].area, rel=1e-8)
    assert A1 == pytest.approx(shape._shapes[1].area, rel=1e-8)



def test_m03():
    shape, properties = ShapeM03()

    A_gross = 0.0
    A_rebar = 0.0
    A_core  = 0.0

    for fiber in shape.create_fibers(group="rebar"):
        A_rebar += fiber["area"]
        A_gross += fiber["area"]

    for fiber in shape.create_fibers(group="core"):
        A_core  += fiber["area"]
        A_gross += fiber["area"]
    
    for fiber in shape.create_fibers(group="cover"):
        A_gross += fiber["area"]

    

    assert A_rebar == pytest.approx(properties["rebar"]["A"], rel=1e-8)
    assert A_gross == pytest.approx(properties["gross"]["A"], rel=1e-8)


