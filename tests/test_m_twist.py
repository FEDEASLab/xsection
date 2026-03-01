"""
Verification against an analytic solution for an elliptical cross-section with a hole, 
as described in:

https://hal.science/hal-00634694/document

"""

import math 
import numpy as np
from xsection import CompositeSection, PolygonSection
from xara import Material
from xsection.library import Ellipse
from xsection.analysis import SaintVenantSectionAnalysis, ElasticAnalysis

class EllipseSolution:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def prandtl(self):
        a = self.a
        b = self.b
        C = a**2*b**2/(a**2 + b**2)
        return lambda x, y: C*(1 - (x/a)**2 - (y/b)**2)
    

# def test_c_twist():
if __name__ == "__main__":
    import veux
    poisson = -0.5
    a = 1
    b = 2
    lam1 = 0.75
    alpha = 1
    beta = 0.01

    soln = EllipseSolution(a, b)
    u = soln.prandtl()

    G = lambda x,y: alpha*math.exp(beta*u(x,y))
    E = lambda x,y: G(x,y)*(2*(1+poisson))

    el = Ellipse(d=a*2,
                 b=b*2, 
                hole_width=lam1*a*2, 
                hole_depth=lam1*b*2,
                mesh_scale=1/20, 
                mesher="triangle", 
                mesh_type="T3")
    
    # veux.serve(veux.render(el.model))

    shape = CompositeSection(
        [
            PolygonSection(el.model.nodes[cell.nodes], 
                           poisson=poisson,
                           mesh_size=el.model.cell_area(cell.tag),
                           group=f"cell_{cell.tag}")
            for cell in el.model.elems
        ],
        holes=[PolygonSection(el.interior()[0])],
        measure_e = {
            f"cell_{cell.tag}": E(*sum(el.model.nodes[cell.nodes])/3.0) for cell in el.model.elems
        }
    )

    ea = ElasticAnalysis(shape, shape._materials, reference=Material(E=1, G=1))
    print(ea.J)
    # print(shape._analysis.torsion_constant(_imode="fiber")*shape._analysis.cnn()[1,1])

    c = (a**2+ b**2)/(a**2*b**2*beta)
    J = 2*math.pi*(alpha/beta)*a*b*((c + lam1**2)*math.exp((1-lam1**2)/c) - (1 + c))
    print(J)


    artist = veux.create_artist(shape.model, ndf=1)
    artist.draw_surfaces()
    u = shape._analysis.solve_twist()
    u = u/np.max(np.abs(u))/2
    artist.draw_surfaces(state=lambda n: u[n])
    veux.serve(artist)


    

