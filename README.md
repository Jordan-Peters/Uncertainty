# Uncertainty
Uncertainty Calculation and Propagation in Python

uncertainty.py is designed to be imported into a python file (import uncertainty as u), it must be located 
in the same file as python file you are editing. uncertainty.py depends on the following modules:

	Numpy
	Sympy
	Thermo - https://thermo.readthedocs.io/

Thermo.Mixture and Thermo.Chemical must be understood in order to know what can and cannot be passed into some
uncertainty.py functions.

Uncertainty values are calculated using sequential perturbation, there are 3 functions that calculate values 
and associated uncertainty and 4 quality of life functions. 



First, u.uncertainty is a general purpose uncertainty function which requires as inputs uncertainty values, symbolic
variables of interest, values for those symbolic variables, and a function to be used. To find the uncertainty in the 
volume of a cube if the side lengths are 1 cm +/- 0.1 cm the function call would look like this:

l, w, h = symbols('l, w, h')  # define needed variables as symbolic variables using Sympy
unc = u.uncertainty([[0.1, 0.1], [0.1, 0.1], [0.1, 0.1]], [l, w, h], [1, 1, 1], func='l * w * h')

Where the first argument is all uncertainty values needed for the calculation entered based on the order of variables 
with the 'plus' value first followed by the 'minus' value. The second argument is the symbolic variables defined above,
the third argument is what each symbolic variable equals, and finally the function needed to perform the calculation.
This function outputs a list of the volume (unc[0]) and uncertainty (unc[1]). 



The second function is used to determine the uncertainty of an equation of state variable based on uncertainty in 
temperature and pressure and any other value needed to fix the state of the mixture. This is where Thermo.Mixture 
documentation will be handy. This function is useful for an air state where only T and P are needed or fixing the 
state of a mixture such as water and ethanol. For air:

mix = u.uncertainty_mix([[1, 1], [100, 100]], 'air', t, p, 'rho')

Where the uncertainties in temperature and pressure are entered forst (in units of K and Pa respectfully) followed by 
the chemicals that make up the mixture ('air' in this case), temperature in K and Pressure in Pa (pint can be used to 
make unit conversion easier), and the property wanted (density in this case).
This function outputs a list of the density (mix[0]) and uncertainty (mix[1]).



u.uncertainty_mix can also be used on more complicated mixtures such as vodka which is a mixture of water and ethanol.
Here the temperature and pressure is not enough to fix the state of the mixture so the volume frations of the mixture 
components will also be needed. However, any of the following parameters can be used to fix the state in addition to 
tempartature and pressure (u.uncertainty_mix will also work with any of these optional inputs):

	zs : list or dict, optional
	Mole fractions of all components in the mixture [-]

	ws : list or dict, optional
	Mass fractions of all components in the mixture [-]

	Vfls : list or dict, optional
	Volume fractions of all components as a hypothetical liquid phase based on pure component densities [-]

	Vfgs : list, or dict optional
	Volume fractions of all components as a hypothetical gas phase based on pure component densities [-]
	
The function call would look like this:

mix = u.uncertainty_mix([[1, 1], [100, 100], [0.01, 0.01], [0.01, 0.01]], ['water', 'ethanol'], t, p, 'rho', vfls=[0.6, 0.4])

This function also takes into account the uncertainties in the volume fractions of each substance in the mixture and 
propagates these uncertainties through to the density.
This function outputs a list of the density (mix[0]) and uncertainty (mix[1]).



The next function does the same thing but for a pure chemical instead of a mixture. The Thermo.Chemical documentation 
would be good to review. For sodium:

chem = u.uncertainty_chem([[1, 1], [100, 100]], 'sodium', t, p, 'rho')

This function outputs a list of the density (chem[0]) and uncertainty (chem[1]).



Next are the various helper functions that make uncertainty propagation easier. 

mean(list)

takes a list as an input and outputs the mean of the list

combine_uncertainty(u_0, u_c)

takes zero-order uncertainty and instrument uncertainty as inputs and combines them into one uncertainty values using 
the square root of the sum of the squares of each value i.e. sqrt(u_0 ** 2 + u_c ** 2)

combine_multi_uncertainty(list)

takes a list of uncertainty values and combines them, this is useful if a measurement device has more than two sources 
of uncertainty such as a scale that can have up to 3 sources. 
