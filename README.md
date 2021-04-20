# Uncertainty
Uncertainty Calculation and Propagation in Python

Uncertainty.py can be imported as: 

	import uncertainty as u

Uncertainty.py depends on the following modules:

	Numpy - https://numpy.org/doc/
	Sympy - https://docs.sympy.org/latest/index.html
	Thermo - https://thermo.readthedocs.io/

A basic understanding of Thermo.Mixture and Thermo.Chemical are required in order to know what can and cannot be passed into some uncertainty.py functions.

Uncertainty values are calculated using the method of sequential perturbation, there are 3 functions that calculate values and associated uncertainty and 4 quality of life functions. 

The uncertainty Function:

u.uncertainty is a general purpose uncertainty function which requires as inputs uncertainty values, symbolic variables of interest, values for those symbolic variables, and a function to be used. 

In order to find the uncertainty in the volume of an irregular rectangular prism if the side lengths are 3, 5, and 6 cm (length, width and height respecively) with designated uncertainties of 0.1, 0.3, amd 0.5 cm respectfully, the uncertainty function can be used:

	l, w, h = symbols('l, w, h')  # define needed variables as symbolic variables using Sympy
	unc = u.uncertainty([[0.1, 0.1], [0.3, 0.3], [0.5, 0.5]], [l, w, h], [3, 5, 6], func='l * w * h')
	print(unc)

Where the first argument is all uncertainty values needed for the calculation entered as a list of lists entered in the same order as the symbolic variables. In this case uncertainty will return:

	[90.0, 9.716480844420984]

Where the first value (unc[0]) is the voulme of the irregular rectangular prism and the second value (unc[1]) is the uncertainty associated with the volume calculation. This function allows for upper and lower uncertainty bounds to be different, meaning it is just as easy to calculate the volume of an shape with the same dimensions as above but now with uncertainties of +0.1, -0.3 for length +0.2, -0.6 for width, and +0.5, -0.2 for height. 

	l, w, h = symbols('l, w, h')  # define needed variables as symbolic variables using Sympy
	unc = u.uncertainty([[0.1, 0.3], [0.2, 0.6], [0.5, 0.2]], [l, w, h], [3, 5, 6], func='l * w * h')
	print(unc)

The 'plus' part of the uncertainty is always entered first followed by the 'minus' part. For this example, uncertainty will return:

	[90.0, 10.742555561876328]

The final arguement taken by uncertainty is the function used for the calculation entered as a string. The Simplify function from Sympy is used to convert the input string into a symbolic function that can be solved. Because of this, the Sympy mathematical operations must be used, for example may Sympy recognizes 'sqrt' as the square root function so that can be used here. 

The uncertainty_mix Function:

This function is used to determine the uncertainty of an equation of state variable based on uncertainty in temperature and pressure and any other value needed to fix the state of the mixture. This is where a working knowledge of the Thermo.Mixture documentation will come in handy. This function is useful for an air state where only temperature (T) and pressure (P) are needed or for fixing the state of a more complex mixture such as water and ethanol. For air:

	t = 300  # K
	p = 101325  # Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100]], 'air', t, p, 'rho')
	print(mix)

Here, the uncertainties in temperature and pressure are entered first, 1 and 100 (in units of K and Pa respectfully) followed by the chemical(s) that make up the mixture entered as either a string or a list of strings ('air' in this case), temperature in K and Pressure in Pa (I recommend the Pint package to easily convert between different units), and the property wanted which is density ('rho') in this case. Please see the Thermo.Mixture documentation for a list of all state properties that work with this function.  For this example, uncertainty_mix will return:

	[1.176982350013618, 0.0041039853697067445]

u.uncertainty_mix can also be used on more complicated mixtures such as a mixture of water and ethanol (vodka). Here the temperature and pressure are not enough to fix the state of the mixture, in this example the volume frations of the mixture components will be used along with temperature and pressure to fix the state. u.uncertainty_mix is designed to work with many of the mixture parameters listed in the Thermo.Mixture documentation (except Vf_TP), so zs, ws, Vfls, or Vfgs can be used in u.uncertainty_mix. The mixture of water and ethanol will look this:

	t = 300  # K
	p = 101325  # Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100], [0.01, 0.01], [0.01, 0.01]], ['water', 'ethanol'], t, p, 'rho', vfls=[0.6, 0.4])
	print(mix)

This function also takes into account the uncertainties in the volume fractions of each substance in the mixture and propagates their uncertainties through to the density.
This exmple with return:

	[940.6003433130429, 1.3466136127003876]

Density has been used quite a lot, so lets look at another example using the vodka mixture previously established:

	t = 300  # K
	p = 101325  # Pa
	mix = u.uncertainty_mix([[1, 1], [100, 100], [0.01, 0.01], [0.01, 0.01]], ['water', 'ethanol'], t, p, 'Pr', vfls=[0.6, 0.4])
	print(mix)

In this example the Prandtl is the desired function output, here the function will return:

	[35.13063328617595, 0.3777093172589262]

The uncertainty_chem Function:

This function performs a very similar task that u.uncertainty_mix does except this function works for a pure fluids defined in Thermo.Chemical instead of mixtures. Once again, knowledge of the Thermo.Chemical documentation would come in handy here. Uncertainty in an equation of state for nitrogen or argon could be calculated based on:

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


Helper Functions

A variety of helper functions have been included to make uncertainty caluclations slightly less tedious.

The mean Function:

This function will take a list as an input and output the mean of the values contained in the input list.

The combine_uncertainty Function:

This function takes as inputs two values of uncertainty such as zero-order and instrument uncertainty and will output the combined uncertainty. This function squares the two input values, adds them together, and outputs the square root i.e.:

	np.sqrt(u_0 ** 2 + u_c ** 2)

The combine_multi_uncertainty Function:

This function takes a list of uncertainty values as an input and combines them in a similar way to u.combine_uncertainty, this function is handy for when multiply sources of uncertainty are present in a measurement. An example of this could be a scale where resolution, repetition, and linearity uncertainties must all be considered. 

So, what is Sequential Perturbation Anyway?

First of all, I'm so glad you asked <3. Sequential perturbation is a method of calculating uncertainty based on a finite difference analysis. A very wordy example and walk-through of the sequential perturbation method is shown below.

Example: calculate the volume and associated uncertainty of a cube with side lengths of 5 cm +/- 0.5 cm.

u.uncertainty begins by iterating over the list of uncertainty values and creates a list of tuples, for this example the list of tuples will look like this: 

	[(l, 5), (w, 5), (h, 5)]

u.uncertainty then utilizes the subs function from SymPy which sets the zeroth element of each tuple equal to the first element of each tuple and substitutes each into the equation that was input into the function. This result is then stored as the zeroth element of a list that will be the output of u.uncertainty. In this example, this value is 125 with units of cm^3 (lets call it R_0). So far this is fairly simple, now the sequential perturbation method wil be used. This method requires the independent variables to be first increased by their associated uncertainty and then decreased by their associated uncertainty. Or, if the uncertainties for length, width, and height and equal to u_L, u_W, and u_H then u.uncertainty is calculating a list containing R_L^+, R_W^+, and R_H^+ where each element of the list is calculated by using the following equations.

	R_L^+ = (L + u_L) * W * H
	R_W^+ = L * (W + u_W) * H
	R_H^+ = L * W * (H + u_H)

A similar process is followed when decreasing the independent variables by their associated uncertainties, u.uncertainty is calculating a list containing R_L^-, R_W^-, and R_H^- where each element of the list is calculated by using the following equations.

	R_L^- = (L - u_L) * W * H
	R_W^- = L * (W - u_W) * H
	R_H^- = L * W * (H - u_H)

u.uncertainty continues to follow the sequential perturbation method by calculating the difference between each element of the R^+ and R^- lists and the original R_0 value. The differences are stored in the same R^+ and R^- lists, overwritting the previous values containted in these lists. In this example, R_L^+ = 137.5 and the difference between R_L^+ and R_0 is 12.5. Because this example is looking at a cube where all uncertainties are the same, so the list of R^+ values is:

	[137.5, 137.5, 137.5] 

When the differences are calculated the R^+ list becomes:

	[12.5, 12.5, 12.5]

This procedure is replicated for the R^- list. Next, the absolute value of the R^+ list is added element-wise to the absolute value of the R^- list. The resulting value is then divided in half and stored in a new list. For this example, that new list is: 

	[12.5, 12.5, 12.5]

The total uncertainty is then calculated following a similar procedure to the u.combine_multi_uncertainty function, this is done because there is not limit to the number of variables that can be input into u.uncertainty ths there is no limit to the length of this list. The result of this calculation is then appended to the list containing the original R_0 value, this list is then returned out of the function. For this example the output of u.uncertainty is 125 cm^3 +/- 21 cm^3.
