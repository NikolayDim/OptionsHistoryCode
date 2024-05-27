import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import time

# This function calculates the price of an American option (call or put) using a binomial tree model.
def binomial_tree_american(S, K, T, r, sigma, q, N, option_type='call'):
    # S: initial stock price
    # K: strike price
    # T: time to maturity
    # r: risk-free rate
    # sigma: volatility of underlying asset
    # q: continuous dividend yield
    # N: number of time steps in the binomial tree
    # option_type: 'call' for a call option, 'put' for a put option

    # Calculate the time step size
    dt = T / N

    # Calculate the up and down factors
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u

    # Calculate the risk-neutral probability
    p = (np.exp((r - q) * dt) - d) / (u - d)

    # Calculate the discount factor
    disc = np.exp(-r * dt)

    # Initialize the option values matrix
    option_values = np.zeros((N + 1, N + 1))

    # Calculate the option values at the final time step
    for j in range(N + 1):
        if option_type == 'call':
            option_values[N, j] = max(0, S * (u ** j) * (d ** (N - j)) - K)
        else:
            option_values[N, j] = max(0, K - S * (u ** j) * (d ** (N - j)))

    # Backward induction: calculate the option values at each previous time step
    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            # Calculate the option value if it is held
            option_value_if_held = disc * (p * option_values[i + 1, j + 1] + (1 - p) * option_values[i + 1, j])
            if option_type == 'call':
                # For a call option, compare the option value if held with the payoff if exercised
                option_values[i, j] = max(option_value_if_held, S * (u ** j) * (d ** (i - j)) - K)
            else:
                # For a put option, compare the option value if held with the payoff if exercised
                option_values[i, j] = max(option_value_if_held, K - S * (u ** j) * (d ** (i - j)))

    # Return the option value at the initial time step
    return option_values[0, 0]

# This function calculates the price of a European option (call or put) using the Black-Scholes formula.
def black_scholes_european(S, K, T, r, sigma, q, option_type='call'):
    # S: initial stock price
    # K: strike price
    # T: time to maturity
    # r: risk-free rate
    # sigma: volatility of underlying asset
    # q: continuous dividend yield
    # option_type: 'call' for a call option, 'put' for a put option

    # Calculate d1 and d2 parameters used in Black-Scholes formula
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Calculate the price of the option based on its type
    if option_type == 'call':
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    return price

def find_interval(f, a, b):
    while f(a) * f(b) > 0:
        a = a / 2
        b = b * 2
    return a, b

# In your implied_volatility_american function
def implied_volatility_american(S, K, T, r, q, market_price, N, option_type='call'):
    start_time = time.time()  # Start timing

    # Define the objective function for the Brent method
    def objective_function(sigma):
        return binomial_tree_american(S, K, T, r, sigma, q, N, option_type) - market_price

    # Find a suitable interval
    a, b = find_interval(objective_function, 1e-6, 4.0)

    # Use the Brent method to find the root of the objective function
    implied_vol = brentq(objective_function, a, b, xtol=1e-6)

    end_time = time.time()  # End timing
    print(f"Execution time for implied_volatility_american: {end_time - start_time} seconds")

    return implied_vol
# This function calculates the implied volatility of a European option using the Black-Scholes formula and the Brent method for root finding.
def implied_volatility_european(S, K, T, r, q, market_price, option_type='call'):
    start_time = time.time()  # Start timing

    # Define the objective function for the Brent method
    def objective_function(sigma):
        return black_scholes_european(S, K, T, r, sigma, q, option_type) - market_price

    # Use the Brent method to find the root of the objective function
    implied_vol = brentq(objective_function, 1e-6, 4.0, xtol=1e-6)

    end_time = time.time()  # End timing
    print(f"Execution time for implied_volatility_european: {end_time - start_time} seconds")

    return implied_vol

