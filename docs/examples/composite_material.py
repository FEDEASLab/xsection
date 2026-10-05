#!/usr/bin/env python
# coding: utf-8

# # Composite Shapes

# In this example a composite section is built by joining multiple basic shapes.



from xsection import CompositeSection
from xsection.library import Circle, Equigon
import matplotlib.pyplot as plt
import numpy as np



from xara.units.iks import inch, foot, ksi, kip


# ## Concrete Circle

# We begin by specifying the dimensions of our section.



d =  7/8*inch
ds = 2/8*inch # diameter of the shear spiral
cover = 1*inch + ds
diameter = 15*inch
core_radius = diameter/2 - cover - ds - d/2
nr = 20 # number of longitudinal reinforcing bars


# Define the exterior shape
exterior = Circle(diameter/2, z=0,
                  group="cover", divisions=60, mesh_scale=1/80)

interior = Equigon(core_radius, z=1,
                   group="core", divisions=nr, mesh_scale=1/20)


# 
# The reinforcing bars are defined separately as small circles. Because stresses generally don't vary drastically within individual reinforcing bars, we'll use a much coarser circle approximation by setting `divisions=4` and `mesh_scale=2`.
# 
# The location of the first bar is given explicitly, and the remaining bars are generated automatically by evenly spacing them around the core.


# A single representative rebar
one_bar = Circle(d/2, z=2, mesh_scale=1/2, divisions=4, group="rebar")

# Location of the first bar; the rest will be generated 
# by linearly spacing them around an arc 
xr = ((diameter/2) - cover - ds - d/2, 0)

bars = one_bar.linspace(xr, xr, nr, endpoint=False, center=(0,0))


# Finally, we assemble all parts—the cover (`interior`), the core (`exterior`), and the bars—into a single [`CompositeSection`](https://peer-open-source.github.io/xsection/api/composite/xsection.CompositeSection.html).

# In[6]:


# Create the composite section
shape = CompositeSection([
            exterior,
            interior,
            *bars
        ])


# In[7]:


import veux

# In[8]:



# ### Moment-Curvature

# In[ ]:


from xsection.analysis import SectionInteraction
from xara import Material, Section
# Define materials
materials = {
    "core": Material(
        type = "Concrete02",
        Fc  =   7.08*ksi,
        ec0 =  0.00295,
        Fcu =  5*ksi,
        ecu =  0.014
    ),
    "cover": Material(
        type = "Concrete02",
        Fc  =   -6.5*ksi,
        ec0 =  -0.002,
        Fcu =  -0.5*ksi,
        ecu =  -0.005,
        # "lambda": 0.1,
        # "Ft": 0.65*ksi,
        # "Ets": 500. # Tension stiffening
    ),
    "rebar": Material(
        type = "Steel01",
        nu = 0.3,
        E  =   29e3*ksi,
        Fy =     40*ksi,
        b =   0.01
    )
}
section = Section("AxialFiber", shape, materials)

#
# Setup the interaction analysis
#
# Define axial load range
axial = np.linspace(-1200*kip, 250*kip, 15)

si = SectionInteraction(section, axial=axial)

fig, ax = plt.subplots(1,2, sharey=True, constrained_layout=True, figsize=(10, 5))
mmax = []

for n, m, k in si.moment_curvature():
    ax[0].plot(k, np.array(m)/foot, '-')

    # ax[1].plot([n]*len(m), m, '-', lw=0.3, markersize=0.5)
    ax[1].plot([n], [max(m)/foot], 'o')

ax[0].axvline(0, color="k", lw=1)
ax[0].axhline(0, color="k", lw=1)
ax[1].axvline(0, color="k", lw=1)
ax[1].axhline(0, color="k", lw=1)
ax[0].set_xlabel("Curvature, $\\kappa$")
ax[0].set_ylabel("Moment, $M(\\varepsilon, \\kappa)$")
ax[1].set_xlabel("Axial force, $P$");


# In[ ]:





# In[ ]:




