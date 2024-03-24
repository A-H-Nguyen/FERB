# # DELETE ME LATER!
import datetime
import numpy as np
import time

from scipy.interpolate import RegularGridInterpolator

# Define original matrix size and new size
size = 8
new_size = 16

# Create coordinate array for both original and resized matrices
x = np.linspace(0, size - 1, size)
y = x  # Since y coordinates are identical to x

# Create coordinate arrays for the resized matrix
new_x = np.linspace(0, size - 1, new_size)
new_y = new_x  # Since y coordinates are identical to x

# Create meshgrid for the new coordinate arrays
new_X, new_Y = np.meshgrid(new_x, new_y)


def interp(original_matrix):
    test_start = time.time()

    # Create RegularGridInterpolator
    interp_func = RegularGridInterpolator((x, y), original_matrix)

    # Interpolate values for the new coordinates using RegularGridInterpolator
    resized_matrix = interp_func((new_Y, new_X))

    # Display the resized matrix
    # print("Resized Matrix:")
    # print(resized_matrix)

    test_end = time.time()

    return test_end - test_start


num_trials = 100000
print(f"{datetime.datetime.now()}: Begin interpolation test for {num_trials} trials")

test_start = time.time()

runtimes = sum(interp(np.random.randint(0, 30, size=(size, size))) for _ in range(num_trials))

test_end = time.time()

print(f"{datetime.datetime.now()}: Testing complete")
print(f"Total test runtime: {test_end - test_start}\n")
print(f"Average runtime of individual interp() funcs executions: {runtimes/num_trials}\n")
