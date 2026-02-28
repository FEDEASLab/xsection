import pytest
from xsection.library import Rectangle
from xsection.analysis import SaintVenantSectionAnalysis
import math
from numba import jit
import numpy as np


def shear_k_rect(depth, width, nu):
    """
    # S. Ali Faghidian  and Isaac Elishakof (2023)

    Shear correction factor k for a rectangular section with dimensions (h, b)
    and Poisson's ratio nu:

        k = 20 h^2 (2 h^2 + b^2)^2 (1+nu)^2 / D

    where
        D = b^6 nu(5+39 nu)
          + 12 h^6 (8+15 nu+7 nu^2)
          + 4 h^4 b^2 (24+46 nu+21 nu^2)
          + h^2 b^4 (24+57 nu+79 nu^2)

    Parameters
    ----------
    h, b, nu : float
        Section dimensions and Poisson's ratio.

    Returns
    -------
    k : float
    """
    h  = depth/2
    b  = width/2

    num = 20.0 * h**2 * (2.0*h**2 + b**2)**2 * (1.0 + nu)**2
    den = (b**6 * nu * (5.0 + 39.0*nu)
           + 12.0 * h**6 * (8.0 + 15.0*nu + 7.0*nu**2)
           + 4.0 * h**4 * b**2 * (24.0 + 46.0*nu + 21.0*nu**2)
           + h**2 * b**4 * (24.0 + 57.0*nu + 79.0*nu**2))

    return num / den


@jit
def shear_rectangle_renton(depth, width, nu,  M=400, N=400, tol=None, rtol=None, return_meta=False):
    """
      F_S = 6/5 + (nu/(1+nu))^2 * coeff * Σ_{m=0..M-1} Σ_{n=1..N} 1/denom 
    
    where
      coeff = 144 (b/a)^4 / π^6
      denom = (2m+1)^2 n^2 * ( (2m+1)^2 (b/(2a))^2 + n^2 )

    Parameters
    ----------
    G, A : float      Shear modulus and area (>0)
    nu   : float      Poisson's ratio (≠ -1)
    a, b : float      Rectangle parameters used in b/a (>0)
    M, N : int        Truncation limits for m and n
    tol  : float|None Absolute row-contribution tolerance (scaled series part)
    rtol : float|None Relative row-contribution tolerance (scaled series part)
    return_meta : bool  If True, also returns a dict with details

    Returns
    -------
    F_S, K_S  (and optionally meta dict)
    """
    if abs(1.0 + nu) < 1e-15:
        raise ValueError("nu must satisfy (1 + nu) != 0.")

    a = depth / 2
    b = width / 2
    beta  = b / a
    beta2 = beta * beta
    coeff = 144.0 * (beta**4) / (math.pi**6)

    total = 0.0            # Neumaier-compensated sum over rows
    c_tot = 0.0
    last_term = 0.0
    used_M = M

    for m in range(M):
        odd  = 2.0*m + 1.0
        odd2 = odd * odd

        # Row sum over n with compensation
        row = 0.0
        c_row = 0.0
        for n in range(1, N+1):
            n2 = float(n*n)
            denom = (odd2 * n2) * (odd2 * (beta2/4.0) + n2)
            term = 1.0 / denom
            # Neumaier compensation for the row
            t = row + term
            if abs(row) >= abs(term):
                c_row += (row - t) + term
            else:
                c_row += (term - t) + row
            row = t
            last_term = term

        row += c_row

        # Add row to total (Neumaier)
        t = total + row
        if abs(total) >= abs(row):
            c_tot += (total - t) + row
        else:
            c_tot += (row - t) + total
        total = t

        # convergence check per row on the *scaled* series part
        if tol is not None or rtol is not None:
            scaled_row   = coeff * row
            scaled_total = coeff * (total + c_tot)
            abs_ok = (tol  is not None) and (abs(scaled_row) <= tol)
            rel_ok = (rtol is not None) and (abs(scaled_row) <= rtol * abs(scaled_total) if scaled_total != 0 else False)
            if abs_ok or rel_ok:
                used_M = m + 1
                break

    S_series = coeff * (total + c_tot)
    F_S = 6.0/5.0 + (nu / (1.0 + nu))**2 * S_series
    K_S = 1.0 / F_S

    # if return_meta:
    #     return  K_S, {
    #         "used_M": used_M,
    #         "used_N": N,
    #         "last_term_unscaled": last_term,
    #         "series_unscaled": total + c_tot,
    #         "series_scaled": S_series,
    #     }
    return K_S


@jit
def square_shear(depth, width, nu, n_terms=20000):
    """
    Stephen and Levinson / Hutchinson 2001
    """
    a = depth/2
    b = width/2
    Iv = depth**3*width/12 # = (2a)**3 * 2b / 12 = 4a^3*b/3
    Iw = depth*width**3/12 # = (2a) * (2b)**3 / 12 = 4ab^3/3
    A  = depth*width       # = (2a)*(2b) = 4ab

    # Calculate the first part of C_4
    C0 = (4 / 45) * (a**3) * b * (-12 * a**2 - 15 * nu * a**2 + 5 * nu * b**2)

    # Calculate the summation part of C_4
    Csum = 0.0
    for n in range(1, n_terms + 1):
        numerator = 16 * (nu**2) * (b**5) * (n * math.pi * a - b * math.tanh(n * math.pi * a / b))
        denominator = ((n * math.pi)**5) * (1 + nu)
        Csum += numerator / denominator

    # Finalize C_4
    c4 = C0 + Csum

    #
    # Calculate k
    #
    k_numerator = -2 * (1 + nu)

    k_denominator = (9/(4 * (a**5)*b))*c4 + nu*(1 - (b**2 / a**2))
    
    if k_denominator == 0:
        return float('inf')

    k = k_numerator / k_denominator

    return k



def test_T6():
    depth  = 24.0
    name = "rectangle"


    point_poisson = [-0.9, -0.5, 0, 0.3, 0.499]
    point_aspects = [1/2, 1,  2]

    for aspect in point_aspects:
        width = depth/aspect
        print(f"{aspect = }, {depth = }, {width = }")

        shape = Rectangle(d=depth, b=width, mesh_scale=1/15, mesh_type="T6")
        model = shape.model

        for v in point_poisson:
            sv = SaintVenantSectionAnalysis(shape, nu=v, model=model)
            romano = sv.create_trace(form="energetic").sce()


            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-3)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-3)

            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)


def test_T6_material():
    depth  = 24.0
    name = "rectangle"

    E = 10
    point_poisson = [-0.9, -0.5, 0, 0.499]
    point_aspects = [1/2,  2]

    for aspect in point_aspects:
        width = depth/aspect
        print(f"{aspect = }, {depth = }, {width = }")


        for v in point_poisson:
            shape = Rectangle(d=depth, 
                              b=width, 
                              mesh_scale=1/15, 
                              material={"E": E, "G": E/(2*(1+v)), "nu": v},
                              mesh_type="T6")

            sv = SaintVenantSectionAnalysis(shape, nu=v, model=shape.model)
            romano = sv.create_trace(form="energetic").sce()


            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-3)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-3)

            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)



def test_T3():
    depth  = 24.0
    point_poisson = [-0.9, -0.5, 0, 0.3, 0.499]

    point_aspects = [1/2, 1,  2]

    for aspect in point_aspects:
        width = depth/aspect
        print(f"{aspect = }, {depth = }, {width = }")

        shape = Rectangle(d=depth, 
                          b=width, 
                          mesh_scale=1/35,
                          mesh_type="T3",
                          mesher="triangle")
        model = shape.model

        for v in point_poisson:
            sv = SaintVenantSectionAnalysis(shape, nu=v, model=model)
            # cowper = shape._analysis.create_trace(nu=v, form="geometric").sce()
            romano = sv.create_trace(form="energetic").sce()

            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-2)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-2)



            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)


    for aspect in point_aspects:
        width = depth/aspect
        print(f"{aspect = }, {depth = }, {width = }")

        shape = Rectangle(d=depth, 
                          b=width, 
                          mesh_scale=1/15,
                          mesh_type="T3",
                          mesher="gmsh")
        model = shape.model

        for v in point_poisson:
            sv = SaintVenantSectionAnalysis(shape, nu=v, model=model)
            # cowper = shape._analysis.create_trace(nu=v, form="geometric").sce()
            romano = sv.create_trace(form="energetic").sce()

            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-2)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-2)



            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)


# def test_T3():
#     depth  = 24.0
#     point_poisson = [-0.9, -0.5, 0, 0.3, 0.499]

#     point_aspects = [1/2, 1,  2]

#     for aspect in point_aspects:
#         width = depth/aspect
#         print(f"{aspect = }, {depth = }, {width = }")

#         shape = Rectangle(d=depth, b=width, mesh_scale=1/50, mesh_type="T3")
#         model = shape.model

#         for v in point_poisson:
#             sv = SaintVenantSectionAnalysis(shape, nu=v, model=model)
#             # cowper = shape._analysis.create_trace(nu=v, form="geometric").sce()
#             romano = sv.create_trace(form="energetic").sce()


#             assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-2)
#             assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-2)


#             cowper = sv.create_trace(form="geometric").sce()
#             assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)
#             assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-2)



def test_temp():
    import numpy.linalg as la
    from pandas import DataFrame as df

    depth  = 24.0


    point_poisson = [0.33]
    point_aspects = [2]

    for aspect in point_aspects:
        width = depth/aspect
        print(f"{aspect = }, {depth = }, {width = }")

        shape = Rectangle(d=depth, b=width, mesh_scale=1/15, mesh_type="T6")
        model = shape.model
        print(shape.summary())

        for v in point_poisson:
            sv = SaintVenantSectionAnalysis(shape, nu=v, model=model)
            tr = sv.create_trace(form="energetic")

            print(df(sv.iesan_matrix()))
            print(df(tr._energy_matrix()))
            print(df(tr.trace_matrix()))
            print(sv.energy_tensor("g"))
            print(sv.moment_tensor(weight="e"))
            print(tr.shift_shear_gamma())

            print(tr.sce())
            print([
                shear_rectangle_renton(width, depth, v),
                shear_rectangle_renton(depth, width, v)
            ])
            romano = sv.create_trace(form="energetic").sce()
            print(romano)
            print("----")


            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-3)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-3)

            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)


    E = 13

    for aspect in point_aspects:
        width = depth/aspect


        for v in point_poisson:
            shape = Rectangle(d=depth, 
                              b=width, 
                              mesh_scale=1/15, 
                              material={"E": E, "G": E/(2*(1+v))},
                              mesh_type="T6")
            
            # print(sv.moment_tensor(weight="e"))

            sv = SaintVenantSectionAnalysis(shape, model=shape.model)
            C = np.zeros((6,6))
            C[:3,:3] = np.eye(3)*1/E
            C[3:,3:] = np.eye(3)*1/(E/(2*(1+v)))
            print(df(sv.iesan_matrix()))
            tr = sv.create_trace(form="energetic")
            print(df(tr._energy_matrix()@C))
            print(df(tr.trace_matrix()))
            print(sv.energy_tensor("g")/shape.material["G"])
            print(sv.moment_tensor(weight="e")/shape.material["E"])
            print(la.solve(sv.energy_tensor("g"), sv.moment_tensor(weight="e")))
            print(tr.shift_shear_gamma())
            print(tr.sce())

            romano = sv.create_trace(form="energetic").sce()
            print([
                shear_rectangle_renton(width, depth, v),
                shear_rectangle_renton(depth, width, v)
            ])
            print("====")


            assert romano[0] == pytest.approx(shear_rectangle_renton(width, depth, v), rel=1e-3)
            assert romano[1] == pytest.approx(shear_rectangle_renton(depth, width, v), rel=1e-3)

            cowper = sv.create_trace(form="geometric").sce()
            assert cowper[0] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)
            assert cowper[1] == pytest.approx((10*(1+v))/(12 +11*v), rel=1e-3)


if __name__ == "__main__":

    test_temp()
    test_T3()