# DELETE ME LATER!
import datetime
import random as rand
import numpy as np
import time

from scipy.interpolate import RectBivariateSpline

# Original matrix
size = 8
original_matrix = np.array([[rand.randint(0, 30) for _ in range(size)] for _ in range(size)])

###############################################################################
# These only needs to be called once!

coords = np.linspace(0, 7, size) # Generate x and y coordinates for the original matrix

bicubic_interp = RectBivariateSpline(coords, coords, original_matrix.T) # create interp func

###############################################################################


def interp(new_size: int):
    # Generate x and y coordinates for the new matrix
    new_coords = np.linspace(0, 7, new_size)

    # start_time = time.time()

    # Perform bicubic interpolation to get the values for the new matrix
    new_matrix = bicubic_interp(new_coords, new_coords).T

    # elapsed_time = time.time() - start_time

    # print(f"*** Interpolation for {new_size}-pixel grid\n", 
    #       f" * Elapsed time: {elapsed_time} seconds\n")


    # print(f"{new_matrix}\n-----------------------------------------")


print(f"{datetime.datetime.now()}: Begin interpolation test")

test_start = time.time()

for test_num in range(100000):
    interp(16)

test_end = time.time()

print(f"{datetime.datetime.now()}: Testing complete")
print(f"Total test runtime: {test_end - test_start}")
