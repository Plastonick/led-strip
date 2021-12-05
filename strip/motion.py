import sys

import time
import math
import random
from rpi_ws281x import Color
from stripfactory import StripFactory
from datetime import datetime
from enum import Enum


def get_last_time(file: str) -> datetime:
    try:
        lastmotion_file = open("../data/" + file, "r")
        timestamp, _ = lastmotion_file.readline().split(".")
    except:
        timestamp = 0

    return datetime.fromtimestamp(int(timestamp))


def get_mode() -> str:
    try:
        mode_file = open("../data/kitchenmode", "r")
        mode = mode_file.readline().lower()
    except:
        mode = "none"

    return mode


def get_occupancy() -> bool:
    last_motion_trigger = get_last_time("kitchenmotionon")
    last_motion_stop = get_last_time("kitchenmotionoff")

    is_triggered = last_motion_trigger > last_motion_stop

    now = datetime.now()
    seconds_stopped = (now - last_motion_stop).seconds

    return is_triggered or seconds_stopped < 60


def main_loop(strip, strip_on: bool) -> bool:
    if get_occupancy():
        occupancy = True
        target_brightness = 100
    else:
        occupancy = False
        target_brightness = 0

    # the strip is off and there's no occupancy detected, don't do anything
    if strip_on == False and occupancy == False:
        return False

    mode = get_mode()

    if occupancy:
        if mode == "rainbow":
            rainbow(strip)

            return True
        elif mode == "christmas":
            christmas(strip)

            return True
        elif mode == "flash":
            flash(strip)

            return True
        elif mode == "rain":
            rain(strip)

            return True
        elif mode == "game":
            game(strip)

            return True

    slide_mode = 1

    if slide_mode == 0:
        smooth(strip, target_brightness)
    elif slide_mode == 1:
        pincer(strip, target_brightness)
    else:
        random_life(strip, target_brightness)

    return occupancy


def rainbow(strip):
    for j in range(256):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(20 / 1000.0)


def get_christmas_color():
    gold = (124, 89, 20)
    green = (9, 75, 15)
    red = (122, 18, 20)

    gold_weight = 4
    green_weight = 1
    red_weight = 1

    rand = random.randint(1, gold_weight + green_weight + red_weight)
    if rand <= gold_weight:
        return gold
    elif rand <= gold_weight + green_weight:
        return green
    else:
        return red


def christmas(strip):
    # pixel: bool
    is_on = {}

    # pixel: current magnitude
    turning_off = {}
    turning_on = {}
    scale = 30

    while get_occupancy() and get_mode() == "christmas":
        for i in range(strip.numPixels()):
            rand = random.randint(0, 300)

            if i in turning_on or i in turning_off:
                continue

            if rand == 0:
                if i not in is_on:
                    continue

                c = strip.getPixelColorRGB(i)

                turning_off[i] = [[c.r, c.g, c.b], scale]
            elif rand == 1:
                if i in is_on:
                    continue

                turning_on[i] = [get_christmas_color(), 0]

        complete = []
        for i in turning_off:
            c = turning_off[i][0]
            s = turning_off[i][1] / scale

            strip.setPixelColorRGB(i, int(c[0] * s), int(c[1] * s), int(c[2] * s))

            if turning_off[i][1] == 0:
                complete.append(i)
                del is_on[i]
            else:
                turning_off[i][1] -= 1

        for i in complete:
            turning_off.pop(i)

        complete = []
        for i in turning_on:
            c = turning_on[i][0]
            s = turning_on[i][1] / scale

            strip.setPixelColorRGB(i, int(c[0] * s), int(c[1] * s), int(c[2] * s))

            if turning_on[i][1] == scale:
                is_on[i] = True
                complete.append(i)
            else:
                turning_on[i][1] += 1

        for i in complete:
            turning_on.pop(i)

        strip.show()
        time.sleep(20 / 1000)


def flash(strip):
    while get_occupancy() and get_mode() == "flash":
        for i in range(5):

            for k in range(strip.numPixels()):
                w1 = 200
                if (k + i) % 5 == 0:
                    strip.setPixelColorRGB(k, w1, w1, w1)
                else:
                    strip.setPixelColorRGB(k, 0, 0, 0)

            strip.show()
            time.sleep(100 / 1000)


# this one probably needs some TLC to make it look decent
def rain(strip):
    # wipe all pixels
    pincer(strip, 0)

    r = [70, 150, 214]

    drops = {}

    while get_occupancy() and get_mode() == "rain":
        # always start from a blank slate and re-draw the raindrops
        for i in range(strip.numPixels()):
            strip.setPixelColorRGB(i, 0, 0, 0)

        new_drop = random.randint(0, strip.numPixels() - 1)

        if new_drop not in drops:
            drops[new_drop] = 1

        completed_drops = []
        for i in drops:
            magnitude = drops[i]
            left_pixels = range(i - magnitude - 1, i - magnitude + 1)
            right_pixels = range(i + magnitude - 1, i + magnitude + 1)

            for j in left_pixels:
                strip.setPixelColorRGB(j, r[0], r[1], r[2])

            for j in right_pixels:
                strip.setPixelColorRGB(j, r[0], r[1], r[2])

            if magnitude >= 10:
                completed_drops.append(i)
            else:
                drops[i] += 1

        for i in completed_drops:
            del drops[i]

        strip.show()
        time.sleep(150 / 1000)


def iterate_board(board, n_pixels):
    # detect and solve collisions
    for i in board:
        direction = board[i][0]
        next = (i + direction) % n_pixels
        next_next = (i + (direction * 2)) % n_pixels

        if next in board:
            # switch direction
            board[i][0] = board[i][0] * -1
            board[next][0] = board[next][0] * -1

        if next_next in board:
            # switch direction
            board[i][0] = board[i][0] * -1
            board[next_next][0] = board[next_next][0] * -1

    new_board = {}
    for i in board:
        direction = board[i][0]
        go_to = (i + direction) % n_pixels

        new_board[go_to] = [direction, board[i][1]]

    return new_board


def game(strip):

    n_pixels = strip.numPixels()
    strip_pixels = range(n_pixels)

    board = {}
    # populate players
    direction = 1
    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
    c = 0

    shuffled = list(range(strip.numPixels()))
    random.shuffle(shuffled)

    selected = shuffled[:9]
    selected.sort()

    for i in selected:
        board[i] = [direction, colors[c]]
        direction = -1 * direction
        c = (c + 1) % 3

    while get_occupancy() and get_mode() == "game":
        # clear the board to re-draw
        for i in strip_pixels:
            strip.setPixelColorRGB(i, 0, 0, 0)

        # draw game board
        for i in board:
            strip.setPixelColor(i, board[i][1])

        # iterate board
        # 1s are going left, 2s are going right, the sides wrap
        board = iterate_board(board, n_pixels)

        # display new board, then wait for next turn
        strip.show()
        time.sleep(30 / 1000)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def wipe(strip, color, start_at, end_at, time):
    if start_at < end_at:
        direction = 1
    else:
        direction = -1

    width = abs(end_at - start_at)

    for i in range(start_at, end_at, direction):
        strip.setPixelColor(i, color)

        strip.show()
        time.sleep(time / width)


def pincer(strip, target_brightness):
    factor = target_brightness / 255
    color = Color(
        math.floor(255 * factor), math.floor(212 * factor), math.floor(106 * factor)
    )

    left_pixels = 153
    right_pixels = strip.numPixels() - left_pixels

    product = left_pixels * right_pixels

    left_index = 0
    right_index = strip.numPixels()

    for i in range(1, product + 1):
        if i % right_pixels == 0:
            strip.setPixelColor(left_index, color)
            strip.show()
            left_index += 1

        if i % left_pixels == 0:
            strip.setPixelColor(right_index, color)
            strip.show()
            right_index -= 1

        time.sleep(3 / product)


def smooth(strip, target_brightness):
    current_brightness = strip.getBrightness()
    color = Color(120, 100, 50)

    for i in range(strip.numPixels() + 1):
        strip.setPixelColor(i, color)

    while current_brightness != target_brightness:
        direction = int(
            (target_brightness - current_brightness)
            / abs(target_brightness - current_brightness)
        )

        current_brightness += direction

        strip.setBrightness(current_brightness)
        time.sleep(0.02)

        strip.show()

    strip.show()


def random_life(strip, target_brightness):
    factor = target_brightness / 255
    color = Color(
        math.floor(255 * factor), math.floor(212 * factor), math.floor(106 * factor)
    )

    pixels = list(range(strip.numPixels()))
    random.shuffle(pixels)

    for i in pixels:
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(0.025)


if __name__ == "__main__":
    try:
        strip = StripFactory().create_strip()
        strip.begin()

        strip_on = False

        while 1:
            strip_on = main_loop(strip, strip_on)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting by user request.")
        sys.exit(0)
