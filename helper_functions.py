import pickle

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