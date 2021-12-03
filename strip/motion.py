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


def main_loop(strip, strip_on: bool) -> bool:
    last_motion_trigger = get_last_time("kitchenmotionon")
    last_motion_stop = get_last_time("kitchenmotionoff")

    is_triggered = last_motion_trigger > last_motion_stop

    now = datetime.now()
    seconds_stopped = (now - last_motion_stop).seconds

    if is_triggered or seconds_stopped < 60:
        occupancy = True
        target_brightness = 100
    else:
        occupancy = False
        target_brightness = 0

    if strip_on == False and occupancy == False:
        return False

    mode = get_mode()

    if mode == "rainbow" and occupancy:
        rainbow(strip)

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