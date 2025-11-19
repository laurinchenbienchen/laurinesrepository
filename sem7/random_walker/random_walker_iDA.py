import numpy as np
import matplotlib.pyplot as plt
import random
import math

# Aufgabe 1: 2D Random Walker
def random_walker(n):
    x = np.zeros(n)
    y = np.zeros(n)

    for i in range(1, n):
        direction = random.randint(0, 3)
        step = random.randint(1, 5)

        if direction == 0:        # hoch
            x[i] = x[i-1] + step
            y[i] = y[i-1]
        elif direction == 1:      # runter
            x[i] = x[i-1] - step
            y[i] = y[i-1]
        elif direction == 2:      # links
            x[i] = x[i-1]
            y[i] = y[i-1] - step
        else:                     # rechts
            x[i] = x[i-1]
            y[i] = y[i-1] + step

    plt.figure(figsize=(6,6))
    plt.plot(x, y, marker="o", markersize=2)
    plt.title(f"2D Random Walk ({n} steps)")
    plt.grid(True)
    plt.show()

random_walker(100)
random_walker(50)

