import RPi.GPIO as GPIO #Library to interact with GPIO pins
import time             #Library for time functions
import datetime         #Library for Timestamping    

# Define GPIO pin for the Geiger counter input
# As specified in PiGI Schematic - Physical Pin 7 - BCM pin GPIO4
GEIGER_PIN = 4

# Setup GPIO
GPIO.setmode(GPIO.BCM)
#GEIGER_PIN configured as input with a pull-up resistor
GPIO.setup(GEIGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize counter - keeps track of number of falling edges detected
count = 0

# Function to handle falling edge interrupt
def falling_edge_callback(channel):
    global count
    count += 1
    print(f"Falling edge detected! Count: {count}")

# Add falling edge detection event
GPIO.add_event_detect(GEIGER_PIN, GPIO.FALLING, callback=falling_edge_callback, bouncetime=300) 
#Bounce time in milliseconds - Used to avoid false triggering due noise
#Trial with bounce time to just more than GMT dead time + recovery time 

try:
    # Run the script indefinitely
    while True:
        # Log counts to a file with a time stamp
        with open("geiger_log.txt", "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - Counts: {count}\n")

        # Wait for a while before logging again
        # Divide by value to get cps or times by different value to get cpm
        time.sleep(10)

except KeyboardInterrupt:
    print("\nScript terminated by user.")
finally:
    # Cleanup GPIO
    GPIO.cleanup()


#Tested on RPi, PiGI and Leybold detector
#Detects falling edges w/ cumulative count
#Speeds up when lantern close to window - def detecting radiation
#needs to be tuned

#Publish time stamp and counts to ROS topic
#RUN AS ROOT (SUDO) ON Pi TO ACCESS GPIO
