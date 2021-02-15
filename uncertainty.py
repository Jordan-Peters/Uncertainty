from sympy import simplify
import numpy as np
from thermo import Mixture, Chemical


def uncertainty(unc_vals, avg_vars, avg_vals, func):

    """Calculates Uncertainty using Sequential Perturbation"""

    # Example Input --> uncertainty([[1, 1]], [x], [2], func='x + 2'), unc_vals = [[+val, -val]]
    func = simplify(func)
    ro_plus = []
    ro_minus = []
    ri = []
    pairs = []
    pairs_2 = []
    # avg
    for i in range(len(avg_vars)):
        pairs.append((avg_vars[i], avg_vals[i]))  # [(x, 2), (y, 3)] etc.
        pairs_2.append((avg_vars[i], avg_vals[i]))
    ro = func.subs(pairs)
    # (+)
    for i in range(len(avg_vars)):
        pairs[i] = (avg_vars[i], avg_vals[i] + unc_vals[i][0])
        ro_plus.append(func.subs(pairs))
        pairs[i] = pairs_2[i]
    for i in range(len(ro_plus)):
        ro_plus[i] = ro_plus[i] - ro
    pairs = []
    pairs_2 = []
    # reset pairs list
    for i in range(len(avg_vars)):
        pairs.append((avg_vars[i], avg_vals[i]))  # [(x, 2), (y, 3)] etc.
        pairs_2.append((avg_vars[i], avg_vals[i]))
    # (-)
    for i in range(len(avg_vars)):
        pairs[i] = (avg_vars[i], avg_vals[i] - unc_vals[i][1])
        ro_minus.append(func.subs(pairs))
        pairs[i] = pairs_2[i]
    for i in range(len(ro_minus)):
        ro_minus[i] = ro_minus[i] - ro
    # ri
    for i in range(len(ro_plus)):  # len(ro_plus) == len(ro_minus)
        ri.append((abs(ro_plus[i]) + abs(ro_minus[i])) / 2)
    # u_r
    ur = 0
    for i in range(len(ri)):
        ur += ri[i] ** 2
    ur = np.sqrt(float(ur))
    sol = [float(ro), ur]
    return sol


def uncertainty_mix(unc_vals, substance, temp, pres, attribute, *args, **kwargs):

    """Calculates Uncertainty from an Equation of State using Sequential Perturbation and Thermo.Mixture"""

    # temp and pres must be input as K and Pa respectively.
    # Example Input --> uncertainty([[1, 1], [2, 2]], 300, 101325, 'air', 'rho), unc_vals = [[+val, -val]]
    # [[+temp_u, -temp_u], [+pres_u, -pres_u]]
    # if air enter 'air', if mixture enter ['water', 'ethanol']

    global add_lst
    zs = kwargs.get('zs', None)  # Mole fractions of components in the mixture
    ws = kwargs.get('ws', None)  # Mass fractions of components in the mixture
    vfls = kwargs.get('vfls', None)  # Volume fractions of components as a hypothetical liquid phase based on pure component densities
    vfgs = kwargs.get('vfgs', None)  # Volume fractions of components as a hypothetical gas phase based on pure component densities

    unc_plus = []
    unc_minus = []

    if type(substance) is list:
        if zs is not None:
            add_lst = add_args(unc_vals, substance, temp, pres, attribute, [zs, None, None, None])
        if ws is not None:
            add_lst = add_args(unc_vals, substance, temp, pres, attribute, [None, ws, None, None])
        if vfls is not None:
            add_lst = add_args(unc_vals, substance, temp, pres, attribute, [None, None, vfls, None])
        if vfgs is not None:
            add_lst = add_args(unc_vals, substance, temp, pres, attribute, [None, None, None, vfgs])
        unc_plus += add_lst[0]
        unc_minus += add_lst[1]

    mix = Mixture(substance, zs=zs, ws=ws, Vfls=vfls, Vfgs=vfgs, T=temp, P=pres)
    # (+)
    mix_u = Mixture(substance, zs=zs, ws=ws, Vfls=vfls, Vfgs=vfgs, T=temp + unc_vals[0][0], P=pres)
    unc_plus.append(getattr(mix_u, attribute))

    mix_u = Mixture(substance, zs=zs, ws=ws, Vfls=vfls, Vfgs=vfgs, T=temp, P=pres + unc_vals[1][0])
    unc_plus.append(getattr(mix_u, attribute))
    # (-)
    mix_u = Mixture(substance, zs=zs, ws=ws, Vfls=vfls, Vfgs=vfgs, T=temp - unc_vals[0][1], P=pres)
    unc_minus.append(getattr(mix_u, attribute))

    mix_u = Mixture(substance, zs=zs, ws=ws, Vfls=vfls, Vfgs=vfgs, T=temp, P=pres - unc_vals[1][1])
    unc_minus.append(getattr(mix_u, attribute))

    for z in range(2):
        unc_plus[z] = unc_plus[z] - getattr(mix, attribute)
        unc_minus[z] = unc_minus[z] - getattr(mix, attribute)

    delta = []
    for z in range(2):
        delta.append((abs(unc_plus[z]) + abs(unc_minus[z])) / 2)

    ur = 0
    for z in range(2):
        ur += delta[z] ** 2
    ur = np.sqrt(float(ur))
    sol = [getattr(mix, attribute), ur]
    return sol


def add_args(unc_vals, substance, temp, pres, attribute, var):

    """Called by uncertainty_mix to Handle Additional Sources of Uncertainty"""

    unc_plus_add = []
    unc_minus_add = []

    ind = var.index(next(item for item in var if item is not None))

    for z in range(len(substance)):
        # (+)
        var[ind][z] += unc_vals[z + 2][0]
        mix_u = Mixture(substance, zs=var[0], ws=var[1], Vfls=var[2], Vfgs=var[3], T=temp, P=pres)
        unc_plus_add.append(getattr(mix_u, attribute))
        var[ind][z] -= unc_vals[z + 2][0]
        # (-)
        var[ind][z] -= unc_vals[z + 2][1]
        mix_u = Mixture(substance, zs=var[0], ws=var[1], Vfls=var[2], Vfgs=var[3], T=temp, P=pres)
        unc_minus_add.append(getattr(mix_u, attribute))
        var[ind][z] += unc_vals[z + 2][1]
    return [unc_plus_add, unc_minus_add]


def uncertainty_chem(unc_vals, substance, temp, pres, attribute):

    """Calculates Uncertainty from an Equation of State using Sequential Perturbation and Thermo.Chemical"""

    # temp and pres must be input as K and Pa respectively.
    # Example Input --> uncertainty([[1, 1], [2, 2]], 300, 101325, 'air', 'rho), unc_vals = [[+val, -val]]
    # [[+temp_u, -temp_u], [+pres_u, -pres_u]]

    unc_plus = []
    unc_minus = []

    chem = Chemical(substance, T=temp, P=pres)
    # (+)
    chem_u = Mixture(substance, T=temp + unc_vals[0][0], P=pres)
    unc_plus.append(getattr(chem_u, attribute))

    chem_u = Mixture(substance, T=temp, P=pres + unc_vals[1][0])
    unc_plus.append(getattr(chem_u, attribute))
    # (-)
    chem_u = Mixture(substance, T=temp - unc_vals[0][1], P=pres)
    unc_minus.append(getattr(chem_u, attribute))

    chem_u = Mixture(substance, T=temp, P=pres - unc_vals[1][1])
    unc_minus.append(getattr(chem_u, attribute))

    for z in range(2):
        unc_plus[z] = unc_plus[z] - getattr(chem, attribute)
        unc_minus[z] = unc_minus[z] - getattr(chem, attribute)

    delta = []
    for z in range(2):
        delta.append((abs(unc_plus[z]) + abs(unc_minus[z])) / 2)

    ur = 0
    for z in range(2):
        ur += delta[z] ** 2
    ur = np.sqrt(float(ur))
    sol = [getattr(chem, attribute), ur]

    return sol


def mean(lst):

    """Calculates Mean values for Uncertainty calculation"""

    s = sum(lst)
    length = len(lst)
    avg = s / length
    return avg


def combine_uncertainty(u_0, u_c):

    """Combines Zero-Order and Instrument Uncertainty Values"""

    u_d = np.sqrt(u_0 ** 2 + u_c ** 2)
    return u_d


def combine_multi_uncertainty(unc_lst):

    """Combines Uncertainty Values From More Than Two Sources"""

    ur = 0
    for i in range(len(unc_lst)):
        ur += unc_lst[i] ** 2
    ur = np.sqrt(float(ur))
    return ur
