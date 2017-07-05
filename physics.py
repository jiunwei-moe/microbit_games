import microbit
import math

# ================================================================================
# Drawing library
# ================================================================================

MAX_BRIGHTNESS = 9


def add_pixel(image, x, y, brightness):
    """ Adds the given brightness to the image at int coordinates (x, y). """
    current = image.get_pixel(x, y)
    image.set_pixel(x, y, min(round(current + brightness), MAX_BRIGHTNESS))


def plot(image, x, y):
    """
    Draws an anti-aliased pixel at float coordinates (x, y).
    Simple algorithm from: https://en.wikipedia.org/wiki/Spatial_anti-aliasing
    """
    width = image.width()
    height = image.height()
    for round_x in range(math.floor(x), math.ceil(x) + 1):
        if round_x < 0 or round_x >= width:
            continue
        for round_y in range(math.floor(y), math.ceil(y) + 1):
            if round_y < 0 or round_y >= height:
                continue
            percent_x = 1 - abs(x - round_x)
            percent_y = 1 - abs(y - round_y)
            percent = percent_x * percent_y
            add_pixel(image, round_x, round_y, percent * MAX_BRIGHTNESS)


def line(image, start_x, start_y, end_x, end_y):
    """
    Draws line between float coordinates (start_x, start_y) and (end_x, end_y).
    """
    delta_x = end_x - start_x
    delta_y = end_y - start_y
    max_t = round(math.sqrt(delta_x * delta_x + delta_y * delta_y))
    if max_t == 0:
        plot(image, (start_x + end_x) / 2, (start_y + end_y) / 2)
        return
    for t in range(max_t + 1):
        plot(image, start_x + delta_x * t /
             max_t, start_y + delta_y * t / max_t)


def circle(image, x, y, r):
    """ Draws empty circle of radius r centered at float coords (x, y). """
    max_t = round(2 * math.pi * r)
    for t in range(max_t):
        plot(image, x + r * math.cos(2 * math.pi * t / max_t),
             y + r * math.sin(2 * math.pi * t / max_t))


def fill_circle(image, x, y, r):
    """ Draws filled circle of radius r centered at float coords (x, y). """
    width = image.width()
    height = image.height()
    r_squared = r * r
    min_x = math.ceil(x - r)
    max_x = math.floor(x + r)
    min_y = math.ceil(y - r)
    max_y = math.floor(y + r)
    for round_x in range(min_x, max_x + 1):
        if round_x < 0 or round_x >= width:
            continue
        for round_y in range(min_y, max_y + 1):
            if round_y < 0 or round_y >= height:
                continue
            dx = round_x - x
            dy = round_y - y
            if dx * dx + dy * dy < r_squared:
                image.set_pixel(round_x, round_y, MAX_BRIGHTNESS)
    circle(image, x, y, r)


# ================================================================================
# Physics simulation
# ================================================================================

COR = 0.8
MIN_DT = 0.1
EPSILON = 0.001


def solve_quad(a, b, c):
    """ Gives a tuple of solutions for ax^2 + bx + c = 0. """
    discriminant = math.sqrt(b * b - 4 * a * c)
    solution_1 = (-b - discriminant) / (2 * a)
    solution_2 = (-b + discriminant) / (2 * a)
    return (solution_1, solution_2) if solution_1 < solution_2 \
        else (solution_2, solution_1)


def simulate(x, u, a, dt, max_x):
    """ Returns tuple of new x, v and dt after one-dimensional simulation. """
    new_x = x + u * dt + 0.5 * a * dt * dt
    if new_x < 0:
        if a != 0:
            (solution_1, solution_2) = solve_quad(0.5 * a, u, x)
            solution = solution_1 if solution_1 > 0 else solution_2
        else:
            solution = -x / u
        v = -COR * (u + a * solution)
        return (EPSILON, v, dt - solution)
    elif new_x > max_x:
        if a != 0:
            (solution_1, solution_2) = solve_quad(0.5 * a, u, x - max_x)
            solution = solution_1 if solution_1 > 0 else solution_2
        else:
            solution = (max_x - x) / u
        v = -COR * (u + a * solution)
        return (max_x - EPSILON, v, dt - solution)
    else:
        return (new_x, u + a * dt, 0)


last_t = microbit.running_time()
x = 2
y = 2
vx = 0
vy = 0
while True:
    t = microbit.running_time()
    dt = (t - last_t) / 1000
    if dt < MIN_DT:
        continue
    last_t = t

    ax = microbit.accelerometer.get_x() / 5
    ay = microbit.accelerometer.get_y() / 5

    # Repeat while there is still time left to simulate
    while dt > 0:
        candidate_x = simulate(x, vx, ax, dt, 4)
        candidate_y = simulate(y, vy, ay, dt, 4)
        if candidate_x[2] == candidate_y[2]:
            (x, vx, dt) = candidate_x
            (y, vy, _) = candidate_y
        elif candidate_x[2] > candidate_y[2]:
            (y, vy, _) = simulate(y, vy, ay, dt - candidate_x[2], 4)
            (x, vx, dt) = candidate_x
        else:
            (x, vx, _) = simulate(x, vx, ax, dt - candidate_y[2], 4)
            (y, vy, dt) = candidate_y

    image = microbit.Image(5, 5)
    plot(image, x, y)
    microbit.display.show(image)
