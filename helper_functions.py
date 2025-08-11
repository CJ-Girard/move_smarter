import pickle
import numpy as np

def load_prms(type='rr'): #rr for random-robust, the description of the rist pre-set pkl file we created
    if type == 'rr':
        file_path = 'random_constraints_robust.pkl'

    #And we leave this space for whatever other types we may want to add later.

    with open(file_path, 'rb') as file:
        prms = pickle.load(file)

    file.close()

    #Originally, the x matrix was (4, 1, n) with n being the number of demographics.
    #Based on new mathematical implementation, here is a better format (axis rearrangement, predominantly due to matrix broadcasting)
    prms['x'] = np.transpose(prms['x'], (2, 1, 0)) #This corrects the matrix structure (notice 1 precedes 0) and moves the pages to the 0th dimension. When the object's dimension is greater than 2, numpy will perform 2D matrix multiplication on the last two axes, so the 0th axis must be the matrix index. The pickle file was already generated; hence we have some broad rearranging to do.

    return prms

def get_scalars(prms):
    sclrs = {}

    scalar_names = [
        "t_max", # Max Allowable Travel Time (hrs)
        "g", # Congestion Weighting Constant (Unitless)
        "h_w", # Wind Average Constant (kW)
        "h_s", # Solar Average Constant (kW)
        "l_b", # Baseline Average Load (kW)
        "gamma", # System Energy Peaker Inefficiency/Marginal Cost Incerase ($/kW^2)
        "p_bse", # Baseline Price per kWh ($/kWh) (Going off of use of renewables)
        "i", # System population
        "w", # Weather conditions
        "lf", # Load Factor
        "rm", # Reserve Margin
        ]

    for i, scalar_name in enumerate(scalar_names):
        try:
            sclrs[scalar_name] = prms["a"][i]
            print(f"Successfully assigned value to {scalar_name} as {sclrs[scalar_name]}")
        except Exception as e:
            print(f"Error reading sheet {i+1}: {e}")

    return sclrs

def generate_T(prms):
    #First, we need to take the default T from the pickle's prms and udplicate it accross a new, 3rd dimension to represent the new dimension, demographics.
    #As of the following line, the mode-distance breakdown (optimization variable) T is the same for each demographic.
    T = prms["T"].reshape((prms["T"].shape[0], prms["T"].shape[1], 1)).repeat(prms['n'], axis=2)

    #Next, in accordance with how numpy broadcasts matrix multiplication for objects with more than 2 dimensions, we need to rearrange the axes of T so that the first axis is the demographic index, and the matrix structure remains the same in the last two axes.
    T = np.transpose(T, (2, 0, 1)) 

    #With this, we see how many kms traveled the default T yields for each distance bucket (axis 1), with a repeated instance to allow for direct comparison/calculation against the real min value, prms['x']
    x_check = np.sum(T, axis=1) 
    x_check = x_check.reshape(x_check.shape[0], 1, x_check.shape[1])

    #We calculate what each distance bucket (axis 2) of T would need to be multiplied by to achieve min miles constraint in that demographic bucket, if necessary (i.e., if it's short)
    multiply = ((x_check/prms['x']) ** -1)
    #Then, we are going to keep this around in case we want to check if it makes a difference in our results; this would ignore all the values that scale *down* T to keep surplus kms in the initial guess.
    # multiply = np.where(multiply<1, 1, multiply)

    #Great! I'm excited! All that's left here is to adjust T appropriately to give us a good start relative to our kms needed constraint.
    T *= multiply

    return T