import microbit
import random

# Length and height of display
N = 5

# Starting delay between gem drops
DROP_DELAY_START = 1000

# Starting delay between gem spawns
SPAWN_DELAY_START = 2000

while True:
    # Current score
    score = 0

    # List of gems
    # Each gem is a pair of x and y coordinates
    gems = []

    # Position (x-coordinate) of player
    player = N // 2

    # Time of next drop
    next_drop = 0

    # Time delay between drops
    drop_delay = DROP_DELAY_START

    # Time of next spawn
    next_spawn = 0

    # Time delay between spawns
    spawn_delay = SPAWN_DELAY_START

    # Image to display
    img = microbit.Image(('0' * N + ':') * N)

    while True:
        t = microbit.running_time()

        if t >= next_drop:
            img = img.shift_down(1)
            game_over = False
            for gem in gems:
                gem[1] += 1
                if gem[1] == 0:
                    img.set_pixel(gem[0], 0, 5)
                elif gem[1] == N:
                    game_over = True
                    break
            if game_over:
                break
            next_drop = t + drop_delay
        else:
            img.set_pixel(player, N - 1, 0)

        if t >= next_spawn:
            gems += [[random.randint(0, N - 1), -1]]
            next_spawn = t + spawn_delay

        # Move player according to input
        if microbit.button_a.was_pressed():
            player = max(player - 1, 0)
        if microbit.button_b.was_pressed():
            player = min(player + 1, N - 1)
        img.set_pixel(player, N - 1, 9)

        # Check if player has caught gem
        index = len(gems) - 1
        while index >= 0:
            gem = gems[index]
            if gem[0] == player and gem[1] == N - 1:
                gems = gems[:index] + gems[index + 1:]
                score += 1
                # Decrease drop delay with each catch
                drop_delay = max(500, DROP_DELAY_START / (1.05 ** score))
                # Decrease spawn delay only after a certain score
                if score > 15:
                    spawn_delay = \
                        max(500, SPAWN_DELAY_START / (1.05 ** (score - 15)))
            index -= 1

        microbit.display.show(img)

    microbit.display.scroll('Score: ' + str(score))
