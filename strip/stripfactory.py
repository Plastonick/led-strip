from rpi_ws281x import *


class StripFactory:
    def create_strip(self) -> Adafruit_NeoPixel:
        LED_COUNT = 286      # Number of LED pixels.
        LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10      # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        return Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL
        )
