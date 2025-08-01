import pickle
import numpy as np

def load_prms(type='rr'): #rr for random-robust, the description of the rist pre-set pkl file we created
    if type == 'rr':
        file_path = 'random_constraints_robust.pkl'

    #And we leave this space for whatever other types we may want to add later.

    with open(file_path, 'rb') as file:
        prms = pickle.load(file)

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
    T = prms["T"].reshape((prms["T"].shape[0], prms["T"].shape[1], 1)).repeat(prms['n'], axis=2)

    x_check = np.sum(T, axis=0)
    x_check = x_check.reshape(x_check.shape[0], 1, x_check.shape[1])

    #We calculate what each column (axis 0) of T would need to be multiplied by to achieve min miles constraint in that demographic bucket, if necessary (i.e., if it's short)
    multiply = ((x_check/prms['x']) ** -1)
    multiply = np.where(multiply<1, 1, multiply)

    #This line gets added retroactiely; it fixes the axes of the multiply object by mode (generic; 1) x Bucket (4) X Page/Demographic (n) just like its product, T.
    multiply = np.swapaxes(multiply, 0, 1)

    return T * multiply