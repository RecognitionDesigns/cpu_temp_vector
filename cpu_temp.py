#!/usr/bin/env python3

import anki_vector
import time
import sys
import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    sys.exit("Cannot import RPi: Do `sudo apt-get install python3-dev python3-rpi.gpio` to install")

from anki_vector.util import degrees
from anki_vector import audio

try:
    from gpiozero import CPUTemperature
except ImportError:
    sys.exit("Cannot import gpiozero: Do `pip3 install gpiozero` to install")

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import PIL: Do `python3 -m pip install --upgrade pip` and then `python3 -m pip install --upgrade Pillow` to install")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#set this to the gpio pin that powers your fan
FAN = 25

GPIO.setup(FAN,GPIO.OUT)
GPIO.output(FAN,GPIO.LOW)

cpu = CPUTemperature()

#set this to the time in seconds between temperature readings
interval = 20
#set this to the temperature you want the fan to come on at
high_temp = 60

while True:
    temp1 = (cpu.temperature)
    time.sleep(interval)
    temp2 = (cpu.temperature)
    time.sleep(interval)
    temp3 = (cpu.temperature)
    time.sleep(interval)

    print(str("Temp 1: {:0.1f}".format(temp1)) + "ºc")
    print(str("Temp 2: {:0.1f}".format(temp2)) + "ºc")
    print(str("Temp 3: {:0.1f}".format(temp3)) + "ºc")
    print("----------------------")
    avg_temp = (temp1 + temp2 + temp3)/3

    print(str("Average Temp: {:0.1f}".format(avg_temp)) + "ºc")
    print("----------------------")

    if (avg_temp) >= (high_temp):
        def make_text_image(text_to_draw, x, y, font=None):
            dimensions = (184, 96)
            text_image = Image.new('RGBA', dimensions, (0, 0, 0, 255))
            dc = ImageDraw.Draw(text_image)
            dc.text((x, y), text_to_draw, fill=(255, 0, 0, 255), font=font)
            return text_image

        try:
            font_file = ImageFont.truetype("arial.ttf", 50)
        except IOError:
            try:
                font_file = ImageFont.truetype("Arial.ttf", 50)
            except IOError:
                pass

        face_sum = (str("{:0.1f}".format(avg_temp)) + "ºC")
        text_to_draw = face_sum
        face_image = make_text_image(text_to_draw, 10, 20, font_file)

        with anki_vector.Robot() as robot:
            robot.behavior.set_head_angle(degrees(30.0))
            robot.behavior.set_lift_height(0.0)

            print("Displaying image on Vector's face...")
            screen_data = anki_vector.screen.convert_image_to_screen_data(face_image)
            robot.screen.set_screen_with_image_data(screen_data, 5.0, interrupt_running=True)
            robot.audio.set_master_volume(audio.RobotVolumeLevel.LOW)
            robot.behavior.say_text("Escape Pod Server CPU temperature rising, temperature currently at {:0.1f} degrees centigrade. activating cooling fan".format(avg_temp))
            GPIO.output(FAN,GPIO.HIGH)
            print("Fan running...")

    else:
        GPIO.output(FAN,GPIO.LOW)
        time.sleep(interval)

