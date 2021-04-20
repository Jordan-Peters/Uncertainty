# Uncertainty
Uncertainty Calculation and Propagation in Python

Uncertainty.py can be imported as: 

	import uncertainty as u

Uncertainty.py depends on the following modules:

	Numpy - https://numpy.org/doc/
	Sympy - https://docs.sympy.org/latest/index.html
	Thermo - https://thermo.readthedocs.io/

A basic understanding of the Mixture and Chemical classes are required in order to use uncertainty.py functions.

Uncertainty values are calculated using the method of sequential perturbation, there are 3 functions that calculate values and associated uncertainty and 3 quality of life functions whose use may be beneficial.

The uncertainty Function:

Uncertainty is a general purpose uncertainty function which requires as inputs uncertainty values, symbolic variables of interest, values for those symbolic variables, and a function to be used. 

Example: Finding the volume and uncertainty of an irregular rectangular prism with side lengths 3, 5, and 6 cm (length, width and height respecively) with designated uncertainties of 0.1, 0.3, amd 0.5 cm respectively. The uncertainty function can be used as:
	
	import uncertainty as u
	from sympy import symbols
	
	l, w, h = symbols('l, w, h')  # define needed variables as symbolic variables using Sympy
	unc = u.uncertainty([[0.1, 0.1], [0.3, 0.3], [0.5, 0.5]], [l, w, h], [3, 5, 6], func='l * w * h')
	print(unc)

Where the first argument is all uncertainty values needed for the calculation entered as a list of lists in the same order as the symbolic variables, the second argument is the symbolic variables used in the calculation entered as a list, the third argument is the values each symbolic variable represent which is also entered as a list, and the forth argument is the function used in the calculation entered as a string. In this case uncertainty will return:

	[90.0, 9.716480844420984]

Where the first value unc[0] is the voulme of the prism and the second value unc[1] is the associated uncertainty. 

All uncertainty functions allow for upper and lower uncertainty bounds to be different, meaning it is just as easy to calculate the volume of a shape with the same dimensions as above but now with uncertainties of +0.1, -0.3 for length +0.2, -0.6 for width, and +0.5, -0.2 for height. 

	l, w, h = symbols('l, w, h')
	unc = u.uncertainty([[0.1, 0.3], [0.2, 0.6], [0.5, 0.2]], [l, w, h], [3, 5, 6], func='l * w * h')
	print(unc)

The 'plus' part of the uncertainty is always entered first followed by the 'minus' part. For this example, uncertainty will return:

	[90.0, 10.742555561876328]

The Simplify function from Sympy is used to convert the input string into a symbolic function that can be solved. Because of this, the Sympy mathematical operators must be used, for example Sympy recognizes 'sqrt' as the square root function so that can be used here. 

The uncertainty_mix Function:

This function is used to determine the uncertainty of an equation of state variable based on uncertainty in temperature and pressure and any other value needed to fix the state of the mixture. This function is useful for air where only temperature (T) and pressure (P) are needed to fix the state and a more complex mixture such as water and ethanol. For air:

	t = 300  # +/- 1 K
	p = 101325  # +/- 100 Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100]], 'air', t, p, 'rho')
	print(mix)

Here, the uncertainties in temperature and pressure are entered first, 1 and 100 (in units of K and Pa respectively) followed by the pure fluids that make up the mixture entered as either a string or a list of strings ('air' in this case), temperature in K and Pressure in Pa (I recommend the Pint package to easily convert between different units), and the property wanted which is density ('rho') in this case. For this example, uncertainty_mix will return:

	[1.176982350013618, 0.0041039853697067445]

Where mix[0] is the density of air in units of kg / m ** 3 and mix[1] is the uncertainty in density in similar units.

u.uncertainty_mix can also be used on more complicated mixtures such as a mixture of water and ethanol. Here the temperature and pressure are not enough to fix the state of the mixture, in this example the volume frations of the mixture components will be used along with temperature and pressure to fix the state. u.uncertainty_mix is designed to work with many of the mixture parameters listed in the Thermo.Mixture documentation (zs, ws, Vfls, or Vfgs).

	t = 300  # K
	p = 101325  # Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100], [0.01, 0.01], [0.01, 0.01]], ['water', 'ethanol'], t, p, 'rho', vfls=[0.6, 0.4])
	print(mix)

This function also takes into account the uncertainties in the volume fractions of each substance in the mixture and propagates their uncertainties through to the density. If desired, these uncertainties could be entered as [0, 0], [0, 0].
This exmple with return:

	[940.6003433130429, 1.3466136127003876]

Density has been used quite a lot, so lets look at another example using the water-ethanol mixture previously established:

	t = 300  # K
	p = 101325  # Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100], [0.01, 0.01], [0.01, 0.01]], ['water', 'ethanol'], t, p, 'Pr', vfls=[0.6, 0.4])
	print(mix)

In this example the Prandtl Number is the desired function output, here the function will return:

	[35.13063328617595, 0.3777093172589262]

The uncertainty_chem Function:

This function performs a very similar task that u.uncertainty_mix does except this function works for pure fluids defined in Thermo.Chemical instead of mixtures. Uncertainty in an equation of state for nitrogen or argon could be calculated based on:

	t = 300  # K
	p = 101325  # Pa
	chem = u.uncertainty_chem([[1, 1], [100, 100]], 'nitrogen', t, p, 'rho')
	print(chem)

	[1.138161436128147, 0.003969023352467612]

	t = 300  # K
	p = 101325  # Pa
	chem = u.uncertainty_chem([[1, 1], [100, 100]], 'argon', t, p, 'rho')
	print(chem)

	[1.6237570273514512, 0.005666215436025757]

'nitrogen' or 'N2' could be used here.


Quality of Life Functions

A variety of helper functions have been included to make uncertainty caluclations slightly less tedious.

The mean Function:

This function will take a list as an input and output the mean of the values contained in the input list.

The combine_uncertainty Function:

This function takes as inputs two values of uncertainty such as zero-order and instrument uncertainty and will output the combined uncertainty. This function squares the two input values, adds them together, and outputs the square root i.e.:

	np.sqrt(u_0 ** 2 + u_c ** 2)

The combine_multi_uncertainty Function:

This function takes a list of uncertainty values as an input and combines them in a similar way to u.combine_uncertainty, this function is handy for when multiply sources of uncertainty are present in a measurement. An example of this could be a scale where resolution, repetition, and linearity uncertainties must all be considered. 
