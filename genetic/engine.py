import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import genetic
import imutils
import time

    spots = []

class crawler:
    x = 0
    y = 0
    genes = []
    travel = []

    def __init__(self, position):
        self.x = position[0]
        self.y = position[1]


def add_flags(n, state, start):
    flags = []
    while len(flags) < n:
        try:
            [x, y] = imutils.spawn_random_point(state.shape)
            if x != start[0] and y != start[1]:
                state[x, y, :] = [1, 0, 0]
                flags.append([x, y])
        except IndexError:
            pass
    return flags, state


# CREATE INITIAL STATE
W = 250
H = 250
N_FLAGS = 100
START = [int(W/2), int(H/2)]
WORLD = np.zeros((W, H, 3))
WORLD[START[0], START[1], :] = [1, 1, 1]

# ADD FLAGS
flags, WORLD = add_flags(N_FLAGS, WORLD, START)
plt.imshow(WORLD)
plt.show()

