
<p align="center">
  <a href="https://gallery.stairlab.io/">
    <img src="https://peer-open-source.github.io/xsection/_static/images/M05.png" alt="xsection logo" width="200" >
  </a>
</p>

<hr>

<h3 align="center">xsection</h3>


<p align="center">
  Structural cross section library
  <br>
  <!-- <a href="https://xsection.github.io/"><strong>Documentation »</strong></a> -->
</p>

*xsection* is a Python package designed to streamline engineering tasks involving structural cross sections. 
Features include:

- Automatic generation of fiber input data for simulations with FEDEASLab, *xara*, and *OpenSees*. 
- Calculation of section properties including:
  - **Timoshenko shear correction factors**
  - **Saint Venant and Vlasov torsion constants**
  - **Moment-Curvature** realtions backed by the complete Xara/OpenSees material libraries. 
  - **Interaction surfaces** 
- Standard shape library including the complete [AISC]() steel database and standard [AASHTO-PCI-ASBI]() bridge box girders.

Note: In order to use the GMSH mesher, you must install:

```bash
conda install -c conda-forge libglu gmsh pygmsh
```



## Support


<table align="center">
<tr>

  <td>
    <a href="https://peer.berkeley.edu">
    <img src="https://raw.githubusercontent.com/claudioperez/sdof/master/docs/assets/peer-black-300.png"
         alt="PEER Logo" width="200"/>
    </a>
  </td>

  <td>
    <a href="https://dot.ca.gov/">
    <img src="https://raw.githubusercontent.com/claudioperez/sdof/master/docs/assets/Caltrans.svg.png"
         alt="Caltrans Logo" width="200"/>
    </a>
  </td>

  <td>
    <a href="https://peer.berkeley.edu">
    <img src="https://raw.githubusercontent.com/claudioperez/sdof/master/docs/assets/brace2_logo-new3_ungrouped.svg"
         alt="BRACE2 Logo" width="200"/>
    </a>
  </td>
 
 </tr>
</table>

<p align="center">
  <a href="https://gallery.stairlab.io/">
    <img src="https://veux.io/_static/images/content_images/fedeas.png" alt="FEDEASLab logo" width="200" >
  </a>
</p>
