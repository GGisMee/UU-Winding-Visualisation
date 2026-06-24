import numpy as np
import matplotlib.pyplot as plt

def morph_wave(arg, square_ratio):
    """
    Morphs smoothly between a pure sine wave and a squarish wave.
    
    Parameters:
    arg (array): The input angle/argument (rad).
    square_ratio (float): Value from 0.0 (100% Sine) to 1.0 (Max Square).
    """
    # Ensure ratio stays between 0 and 1
    k = np.clip(square_ratio, 0.0, 1.0)
    
    # Base sine wave (1st harmonic)
    y = np.sin(arg)
    
    # Dynamically add higher odd harmonics based on the square_ratio
    # 20 harmonics is a good sweet spot for a sharp but clean look
    max_harmonics = 20 
    
    for i in range(3, max_harmonics * 2, 2):
        # Scale down how fast higher harmonics kick in using k
        weight = k ** (i / 3) 
        y += (1 / i) * np.sin(i * arg) * weight
        
    # Normalize the peak to 1.0 so the volume/amplitude stays constant

    max_val = np.max(np.abs(y))
    return y / np.maximum(max_val, 1e-12)

X = np.linspace(0,4*np.pi, 100)



def morph_wave_lerp(arg, square_ratio):
    # 1. Generate the perfect targets
    sine_wave = np.sin(arg)
    square_wave = np.sign(sine_wave)

    # 2. Blend them linearly based on the ratio
    y = (1 - square_ratio) * sine_wave + square_ratio * square_wave
    return y

import numpy as np


def morph_wave_adjustable(arg:np.ndarray, square_ratio:float):
    k = np.clip(square_ratio, 0.0, 1.0)
    arg = np.asarray(arg)

    # 1. Strict boundary check for absolute pure sine wave
    if k == 0.0:
        return np.sin(arg)

    # 2. Shape the slider response curve
    # A gamma of 2.5 keeps the steepness low for longer,
    # making the visual growth of the "squareness" feel perfectly linear.
    gamma = 2.5
    k_warped = k**gamma

    # 3. Scale the max steepness (50.0 is incredibly sharp)
    max_steepness = 50.0
    steepness = 1.0 + (k_warped * (max_steepness - 1.0))

    # 4. Generate the tanh wave and normalize it
    y = np.tanh(steepness * np.sin(arg))
    return y / np.tanh(steepness)

@staticmethod
def magnet(arg: np.ndarray) -> np.ndarray:
    return (np.sign(np.sin(arg)) * (np.sin(arg) ** 2) + 0.228 * np.sin(3 * arg)) / 0.7724



Y = np.linspace(0,1,10)
f = lambda x: np.mean(morph_wave_adjustable(X,x)-magnet(X))
plt.plot(Y, [f(y) for y in Y])
print(np.mean(morph_wave_adjustable(X,0.16)-magnet(X)))

plt.plot(X, morph_wave_adjustable(X, 0.16))

plt.plot(X, magnet(X))
plt.plot()
plt.show()