Documentation
^^^^^^^^^^^^^

.. currentmodule:: xsection
   

The :mod:`xsection` package comprises the following core geometry classes:

.. autosummary::

   PolygonSection
   CompositeSection


.. currentmodule:: xsection.library 

The ``xsection.library`` submodule exposes the following convenience classes which inherit from the core geometry classes:

.. autosummary::

   from_aisc <fromAISC>
   Circle <Circle>
   Rectangle <Rectangle>
   WideFlange <WideFlange>
   HalfFlange <HalfFlange>
   Channel <Channel>
   Angle <Angle>
   aisc_data <aiscData>


.. toctree::
   :maxdepth: 1
   :hidden:

   xsection <self>
   library/index
   attributes/index
   methods/index
   polygon/xsection.PolygonSection
   composite/xsection.CompositeSection


.. currentmodule:: xsection

The central abstraction in the :mod:`xsection` package is the :class:`Section` interface,
which is defined by the following attributes:

.. autosummary::

   Section.elastic <elastic>
   Section.centroid <centroid>
   Section.linspace <linspace>
   Section.translate <translate>

