#!/usr/bin/env python
# coding: utf-8

import pytest
import xara
from xsection import CompositeSection
from xara import UniaxialMaterial
from xara.units.iks import inch, foot, ksi, kip
import numpy as np
import veux

from xsection.library import Rectangle, Circle, HollowRectangle
from xsection import CompositeSection

# Define materials
materials = {
    "core": UniaxialMaterial(
        type = "Concrete02",
        Fc  =   7.08*ksi,
        nu  =  0.2,
        ec0 =  0.00295,
        Fcu =  5*ksi,
        ecu =  0.014
    ),
    "cover": UniaxialMaterial(
        type = "Concrete02",
        Fc  =   -6.5*ksi,
        nu  =   0.2,
        ec0 =  -0.002,
        Fcu =  -0.5*ksi,
        ecu =  -0.005,
        # "lambda": 0.1,
        # "Ft": 0.65*ksi,
        # "Ets": 500. # Tension stiffening
    ),
    "rebar": UniaxialMaterial(
        type = "Steel01",
        nu = 0.3,
        E  =   29e3*ksi,
        Fy =     40*ksi,
        b =   0.05
    )
}


def _xara_fibers(section, y=None):
    model = xara.Model(ndm=3, ndf=6)

    # Define two nodes at (0,0)
    model.node(1, (0.0, 0.0, 0))
    model.node(2, (0.0, 0.0, 0))

    # Fix all degrees of freedom except axial and bending
    model.fix(1, (1, 1, 1, 1, 1, 1))
    model.fix(2, (0, 1, 1, 1, 0, 1))

    # Define materials
    for material in materials.values():
        model.material(material)

    # Define section
    model.section(section)

    # Define element
    x = (1.0, 0.0, 0.0)
    if y is None:
        y = (0.0, 1.0, 0.0)
    model.element("ZeroLengthSection", 1, (1, 2), section, y=y, x=x)

    data = model.asdict()

    fibers = data["StructuralAnalysisModel"]["properties"]["sections"][0]["fibers"]

    return dict(fibers=fibers, area=sum(f["area"] for f in fibers))
    

def test_uniaxial_circle():
    circle = Circle(radius=5, material=materials["rebar"])

    # Single centroid point
    section = xara.FrameSection("UniaxialFiber", circle, fibers={"d": 1})
    fibers = _xara_fibers(section)
    assert fibers["area"] == pytest.approx(25 * np.pi, rel=1e-6)

    # Sunflower method
    section = xara.FrameSection("UniaxialFiber", circle, fibers={"r": 4, "rule": "sunflower"})
    fibers = _xara_fibers(section)
    assert fibers["area"] == pytest.approx(25 * np.pi, rel=1e-4)


# ## Rectangle

def _create_rectangle(h, b, c, d):
    bar = Circle(d/2, z=2, 
                material=materials["rebar"],
                mesh_scale=1/2, divisions=4, group="rebar")

    cover = HollowRectangle(b, h, t=c, z=0, 
                            group="cover", 
                            material=materials["cover"]
    )

    core = Rectangle(b-2*c, h-2*c, z=1, 
                    group="core", material=materials["core"])

    shape = CompositeSection([
                cover,
                core,
                *bar.linspace([-b/2+c+d/2, -h/2+c+d/2], [ b/2-c-d/2,-h/2+c+d/2], 3), # Top bars
                *bar.linspace([-b/2+c+d/2,        0], [ b/2-c-d/2,       0], 2), # Center bars
                *bar.linspace([-b/2+c+d/2,  h/2-c-d/2], [ b/2-c-d/2, h/2-c-d/2], 3)  # Bottom bars
            ])

    return shape


def _test_rectangle_fibers():
    # TODO
    h = 24
    b = 15
    d = 7/8
    r = 0 #d/2

    c = 1.5
    shape = _create_rectangle(h, b, c, d)

    layout = {
        "cover": {"d": 10, "t": 3, "b": 5},
        "core":  {"d": 10, "b": 5},
    }

    section = xara.FrameSection("UniaxialFiber", shape, fibers=layout)

    fibers = _xara_fibers(section)

