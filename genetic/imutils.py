import matplotlib.pyplot as plt
import numpy as np
import random
import time


def plot(state):
    f = plt.figure()
    if len(state.shape) == 3:
        plt.imshow(state)
    else:
        plt.imshow(state, 'gray_r')
    plt.show()


def spawn_random_point(dims):
    x = random.randint(0, dims[1])
    y = random.randint(0, dims[0])
    return [x, y]


def flat_map(dims):
    """
    FLAT_MAP is useful for pre-allocating a dictionary of index-to-subscript
    lookups on 2D matrix positions. This is particularly useful if any loop
    contains translating coordinates from a flattened 2D array.
    :param dims:
    :return:
    """
    xmax = dims[0]
    ymax = dims[1]
    ind2sub = {}
    ii = 0
    for x in range(xmax+1):
        for y in range(ymax+1):
          ind2sub[ii] = [x, y]
          ii += 1
    return ind2sub


def draw_centered_box(state, sz, value, show):
    cx = state.shape[0]/2
    cy = state.shape[1]/2
    state[cx-sz:cx+sz,cy-sz:cy+sz] = value
    if show:
        plt.imshow(state)
        plt.show()
    return state


def draw_centered_circle(canvas, radius,value, show):
    cx = canvas.shape[0]/2
    cy = canvas.shape[1]/2
    for x in np.arange(cx - radius, cx + radius, 1):
        for y in np.arange(cy - radius, cy + radius, 1):
            r = np.sqrt((x-cx)**2 + ((cy-y)**2))
            if r <= radius:
                try:
                    canvas[x, y] = value
                except IndexError:
                    pass
    if show:
        plt.imshow(canvas, 'gray_r')
        plt.show()
    return canvas


def angle_between_points(dx, dy):
    # I want vertical to be 0 degrees, so most tangents need offsets
    if (dx and dy) > 0:
        angle = (np.arctan(dy / dx) / (2 * np.pi)) * 360
    if (dx and dy) < 0:
        angle = -90 + (np.arctan(dy / dx) / (2 * np.pi)) * 360
    if dx > 0 > dy:
        angle = (np.arctan(dy / dx) / (2 * np.pi)) * 360 + 90
    if dy > 0 > dx:
        angle = -90 + (np.arctan(dy / dx) / (2 * np.pi)) * 360
    if dx == 0 and dy > 0:
        angle = 0
    if dx == 0 and dy < 0:
        angle = 180
    if dy == 0 and dx > 0:
        angle = 90
    if dy == 0 and dx < 0:
        angle = 270
    return angle


def get_displacement(pt_a, pt_b):
    x1 = pt_a[0];    y1 = pt_a[1]
    x2 = pt_b[0];    y2 = pt_b[1]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)


def create_cloud(n_points, state_in, mass, colors):
    tic = time.time()
    particles = []
    if len(mass) != n_points:
        print '[!] Mass input is not vectorized, or dimensions are incorrect'
        try:
            print mass.shape
        except:
            pass
        exit()
    elif len(colors) != n_points:
        print '[!] Mass input is not vectorized, or dimensions are incorrect'
        exit()
    else:
        count = 0
        dims = np.array(state_in[:, :, 0]).shape
        while len(particles) < n_points:
            try:
                [x, y] = spawn_random_point(dims)
                particles.append([[x, y], mass, colors[count]])
                state_in[x, y, 0] = colors[count][0]
                state_in[x, y, 1] = colors[count][1]
                state_in[x, y, 2] = colors[count][2]
                count += 1
            except IndexError:
                pass
        if 0 < int(time.time()-tic)%30==0:
            print '[%ss Elapsed]' % str(time.time()-tic)
    return particles, state_in


def generate_random_steps(start, n_steps):
    moves = []
    spots = []
    for ii in range(n_steps):
        [x, y] = start
        directions = {1: [x - 1, y - 1], 2: [x, y - 1], 3: [x + 1, y - 1],
                      4: [x - 1, y], 5: [x, y], 6: [x + 1, y],
                      7: [x - 1, y + 1], 8: [x, y + 1], 9: [x + 1, y + 1]}
        mov = random.randint(1, 9)
        moves.append(mov)
        spots.append(directions[mov])
        start = directions[mov]
    return moves, spots


def add_lists(list_a, list_b):
    [list_a.append(e) for e in list_b]
    return list_a


def create_world(dims, flags):
    state = np.zeros((dims[0], dims[1], 3))
    for flag in flags:
        [x,y] = flag
        state[x,y,:] = [1,0,0]
    return state
