import RPi.GPIO as GPIO
import time
import subprocess
    
GREEN_LED  = 22;
RED_LED    = 23;
YELLOW_LED = 24;

BLUE_BUTTON = 17;
RED_BUTTON  = 27;

erase_success_str = b'Erasing done.'
flash_success_str = b'Flash download:'
disconnected_str  = b'Cannot connect to target.'

# Functions for LED status indicators
def flash_green_led():
    GPIO.output(GREEN_LED,  GPIO.HIGH)
    GPIO.output(YELLOW_LED, GPIO.LOW)
    GPIO.output(RED_LED,    GPIO.LOW)

def flash_red_led():
    GPIO.output(GREEN_LED,  GPIO.LOW)
    GPIO.output(YELLOW_LED, GPIO.LOW)
    GPIO.output(RED_LED,    GPIO.HIGH)

def flash_yellow_led():
    GPIO.output(GREEN_LED,  GPIO.LOW)
    GPIO.output(YELLOW_LED, GPIO.HIGH)
    GPIO.output(RED_LED,    GPIO.LOW)

def flash_all_leds():
    GPIO.output(GREEN_LED,  GPIO.HIGH)
    GPIO.output(YELLOW_LED, GPIO.HIGH)
    GPIO.output(RED_LED,    GPIO.HIGH)

def turn_all_leds_off():
    GPIO.output(GREEN_LED,  GPIO.LOW)
    GPIO.output(YELLOW_LED, GPIO.LOW)
    GPIO.output(RED_LED,    GPIO.LOW)

def program_ready_sequence():
    for i in range(3):
        flash_green_led()
        time.sleep(0.35) 
        flash_red_led()
        time.sleep(0.35)
        flash_yellow_led()
        time.sleep(0.35)
    turn_all_leds_off()
    time.sleep(0.5)
    flash_all_leds()
    time.sleep(2)
    turn_all_leds_off()

# Check text for success messages
def check_success(jlink_output, success_string):
    if success_string in jlink_output:
        return 1
    elif disconnected_str in jlink_output:
        return 0
    else:
        return -1

# Flash lights according to flash or erase results
def update_status_leds(val):
    if val == 1:
        flash_green_led()
        time.sleep(5)
        turn_all_leds_off()
    elif val == 0:
        flash_yellow_led()
        time.sleep(5)
        turn_all_leds_off()
    else:
        flash_red_led()
        time.sleep(5)
        turn_all_leds_off()
                  
# Flash the hex file onto the nRF device
def blue_button_callback(channel):
    flash_hex = subprocess.run(["/home/ubuntu/JLink/./JLinkExe", "-device", "nRF52", \
                                "-CommandFile", "/home/ubuntu/flash_nrf/flash_commandfile.jlink"], \
                                stdout=subprocess.PIPE, universal_newlines=False)
    result = check_success(flash_hex.stdout, flash_success_str)
    update_status_leds(result)

# Erase all memory on the nRF device
def red_button_callback(channel):
    flash_hex = subprocess.run(["/home/ubuntu/JLink/./JLinkExe", "-device", "nRF52", \
                                "-CommandFile", "/home/ubuntu/flash_nrf/erase_commandfile.jlink"], \
                                stdout=subprocess.PIPE, universal_newlines=False)
    result = check_success(flash_hex.stdout, erase_success_str)
    update_status_leds(result)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Blue button is gpio 17, Red button is gpio 27
GPIO.setup(BLUE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(BLUE_BUTTON, GPIO.FALLING, callback=blue_button_callback, bouncetime=500)
GPIO.add_event_detect(RED_BUTTON, GPIO.FALLING, callback=red_button_callback, bouncetime=500)

# Green led is gpio 22, red led is gpio 23
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
turn_all_leds_off()
program_ready_sequence()

try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()
