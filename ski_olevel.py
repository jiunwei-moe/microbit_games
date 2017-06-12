# Adapted from Simple Slalom by Larry Hastings
# http://microbit-micropython.readthedocs.io/en/latest/accelerometer.html

import microbit
import random

# Length and height of display
N = 5

# Accelerometer reading that corresponds to left edge
MIN_ACC = -1024

# Accelerometer reading that corresponds to right edge
MAX_ACC = 1024

# Range of valid accelerometer readings
RANGE_ACC = MAX_ACC - MIN_ACC

# Minimum and maximum speed that wall can move from top to bottom of display
WALL_MIN_SPEED = 400
WALL_MAX_SPEED = 100

# Minimum and maximum speed that person can move from left to right
PLAYER_MIN_SPEED = 200
PLAYER_MAX_SPEED = 50

# Maximum score to use for calculating speed
MAX_SPEED = 12

while True:
    # Image of LED pixels  to display
    i = microbit.Image('00000:' * N)

    # Position (x-coordinate) of player
    player_x = N // 2

    # Position (y-coordinate) of wall
    # Varies from -1 to N+2
    wall_y = -1

    # Position (x-coordinate) of hole in wall
    hole = 0

    # Current score
    score = 0

    # Whether current wall has been tested for collision with player yet
    wall_tested = False

    # Initial speeds of wall and player
    wall_speed = WALL_MIN_SPEED
    player_speed = PLAYER_MIN_SPEED

    # Time of next update for wall
    wall_next = 0

    # Time of next update for player
    player_next = 0

    while True:
        t = microbit.running_time()

        if t < player_next and t < wall_next:
            # Not yet time for any updates, so sleep
            delta = min(player_next, wall_next) - t
            microbit.sleep(delta)
            continue

        if t >= player_next:
            # Turn off old pixel
            i.set_pixel(player_x, N - 1, 0)

            # Find target x coordinate based on accelerometer
            acc = microbit.accelerometer.get_x()
            acc = min(max(MIN_ACC, acc), MAX_ACC)
            target_x = ((acc - MIN_ACC) / RANGE_ACC) * N
            target_x = min(max(0, target_x), N - 1)
            target_x = int(target_x + 0.5)

            # Move player if current wall has not been tested
            if not wall_tested:
                if player_x < target_x:
                    player_x += 1
                elif player_x > target_x:
                    player_x -= 1

            # Turn on new pixel
            i.set_pixel(player_x, N - 1, 9)

            # Set time of next update based on speed
            player_next = t + player_speed

        if t >= wall_next:
            if wall_y < N:
                # Erase old wall
                use_wall_y = max(wall_y, 0)
                for wall_x in range(N):
                    if wall_x != hole:
                        i.set_pixel(wall_x, use_wall_y, 0)

            # Update wall position
            wall_y += 1

            # Only generate new wall when old wall reaches y-coordinate N+2
            if wall_y == N + 2:
                wall_y = -1
                hole = random.randrange(N)
                wall_tested = False

            if wall_y < N:
                # Draw new wall if it is visible on display
                use_wall_y = max(wall_y, 0)
                for wall_x in range(N):
                    if wall_x != hole:
                        i.set_pixel(wall_x, use_wall_y, 6)

            # Set time of next update based on speed
            wall_next = t + wall_speed

        if wall_y == N - 1 and not wall_tested:
            wall_tested = True
            if (player_x != hole):
                # Collision! Game over!
                break
            score += 1
            # Calculate new speeds
            speed = min(score, MAX_SPEED)
            wall_speed = WALL_MIN_SPEED + \
                int((WALL_MAX_SPEED - WALL_MIN_SPEED) * speed / MAX_SPEED)
            player_speed = PLAYER_MIN_SPEED + \
                int((PLAYER_MAX_SPEED - PLAYER_MIN_SPEED) * speed / MAX_SPEED)

        microbit.display.show(i)

    microbit.display.show(i.SAD)
    microbit.sleep(1000)
    microbit.display.scroll("Score:" + str(score))

    while True:
        if (microbit.button_a.is_pressed() or microbit.button_b.is_pressed()):
            break
        microbit.sleep(100)
