import microbit

# Length and height of display
N = 5

# Time delay between frames
DELAY = 100

while True:
    # Position (y-coordinate) of each player
    A_position = N // 2
    B_position = N // 2

    # Direction each player will move for next step
    # True for up, False for down
    A_direction = False
    B_direction = True

    # Whether each button was pressed on the previous frame
    A_pressed = False
    B_pressed = False

    # List of bullets on the screen
    # Each bullet is a list of three items
    # Index 0 is its x-coordinate
    # Index 1 is its y-coordinate
    # Index 2 is its direction of travel (-1 for left, +1 for right)
    bullets = []

    # Winner of game, or None if there is no winner yet
    winner = None

    while True:

        if microbit.button_a.is_pressed():
            # Button A is being pressed, so move player
            if A_direction:
                A_position -= 1
            else:
                A_position += 1
            # If player hits edge, reverse direction
            if A_position == 0 or A_position == N - 1:
                A_direction = not A_direction
            # Keep track that Button A was pressed
            A_pressed = True
        elif A_pressed:
            # Button A was just released, so shoot bullet
            bullets += [[0, A_position, +1]]
            # Keep track that Button A was released
            A_pressed = False

        if microbit.button_b.is_pressed():
            # Button B is being pressed, so move player
            if B_direction:
                B_position -= 1
            else:
                B_position += 1
            # If player hits edge, reverse direction
            if B_position == 0 or B_position == N - 1:
                B_direction = not B_direction
            # Keep track that Button B was pressed
            B_pressed = True
        elif B_pressed:
            # Button B was just released, so shoot bullet
            bullets += [[N - 1, B_position, -1]]
            # Keep track that Button B was released
            B_pressed = False

        # Update positions of bullets
        index = len(bullets) - 1
        while index >= 0:
            bullet = bullets[index]
            bullet[0] += bullet[2]
            # If bullet is off the display, remove it
            if bullet[0] < 0 or bullet[0] >= N:
                bullets = bullets[:index] + bullets[index + 1:]
            index -= 1

        # Draw frame of game on display
        microbit.display.clear()
        microbit.display.set_pixel(0, A_position, 9)
        microbit.display.set_pixel(N - 1, B_position, 9)
        for bullet in bullets:
            microbit.display.set_pixel(bullet[0], bullet[1], 5)
            if bullet[0] == 0 and bullet[1] == A_position:
                winner = 'B'
                break
            if bullet[0] == N - 1 and bullet[1] == B_position:
                winner = 'A'
                break
        if winner:
            break
        microbit.sleep(DELAY)

    microbit.display.scroll(winner + ' WIN')
