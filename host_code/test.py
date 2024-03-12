# DELETE ME LATER!

import random as rand
import numpy as np

from scipy.interpolate import interp2d

# Original 8x8 matrix
original_matrix = np.array([[rand.randint(0, 30) for _ in range(8)] for _ in range(8)])

print(f"{original_matrix}\n-----------------------------------------")

# Size of the new matrix
N = 16

# Generate x and y coordinates for the original matrix
x = np.linspace(0, 7, 8)
y = np.linspace(0, 7, 8)

# Generate x and y coordinates for the new matrix
new_x = np.linspace(0, 7, N)
new_y = np.linspace(0, 7, N)

# Create a function for bicubic interpolation
bicubic_interp = interp2d(x, y, original_matrix, kind='cubic')

# Perform bicubic interpolation to get the values for the new matrix
new_matrix = bicubic_interp(new_x, new_y)

print(f"{new_matrix}\n-----------------------------------------")


