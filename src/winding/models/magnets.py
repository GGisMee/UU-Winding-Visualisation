from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import numpy as np


import numpy as np
from dataclasses import dataclass
from enum import Enum

class Magnets(Enum):
    sine = lambda arg: np.sin(arg)
    sinish = lambda arg: (np.sign(np.sin(arg)) * (np.sin(arg) ** 2) + 0.228 * np.sin(3 * arg)) / 0.7724
    squarish = lambda arg: square_sin(arg, 5)
    triangleish = lambda arg: triangle_sine(arg, 0.3)

def square_sin(x:np.ndarray, k:float) -> np.ndarray:
    """A hyperbolic blend function between sin and square with parameter k
    k = 0.1: Almost pure sinewave
    k = 1.0: Smooth square curve
    k = 10.0+: Sharp square curve"""
    return np.tanh(k * np.sin(x)) / np.tanh(k)


def triangle_sine(x, k):
    """
    Linjär interpolation mellan triangel och sinus.
    
    k = 0.0: Perfekt skarp triangelvåg
    k = 0.5: Rundad triangelvåg (typiskt generatorfält)
    k = 1.0: Perfekt sinusvåg
    """
    # Se till att k håller sig inom [0, 1]
    k = np.clip(k, 0.0, 1.0)
    
    # 1. Generera en perfekt triangelvåg (amplitud 1)
    pure_triangle = (2 / np.pi) * np.arcsin(np.sin(x))
    
    # 2. Generera en perfekt sinusvåg (amplitud 1)
    pure_sine = np.sin(x)
    
    # 3. LERP
    return (1.0 - k) * pure_triangle + k * pure_sine
