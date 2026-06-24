import matplotlib.pyplot as plt
from winding.models.magnets import Magnets
import numpy as np

X = np.linspace(0,4*np.pi, 1000)
plt.plot(X,Magnets.triangleish(X))
plt.plot(X,Magnets.squarish(X))
plt.plot(X,Magnets.sinish(X))
plt.plot(X, np.sin(X))
plt.show()