import RPi.GPIO as GPIO
import time
import datetime
import os
import sys
import subprocess
 
GPIO.setmode(GPIO.BCM)
GPIO_PIR = 7
 
print ("PIR Module Test (CTRL-C to exit)")
 
# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)      # Echo
 
Current_State  = 0
Previous_State = 0
 
try:
 
  print ("Waiting for PIR to settle ...")
 
  # Loop until PIR output is 0
  while GPIO.input(GPIO_PIR)==1:
    Current_State  = 0
 
  print ("Ready")
 
  # Loop until users quits with CTRL-C
  while True :
 
    # Read PIR state
    Current_State = GPIO.input(GPIO_PIR)
 
    if Current_State==1 and Previous_State==0:
      # PIR is triggered
      print ("Motion detected!")
      timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
      # Capture a 40 second video
      subprocess.call ("raspivid -o /home/pi/bird/" + "_" + timestamp + ".264 -t 30000", shell=True)
      print ("Captured trailcam" + "_" + timestamp + ".264")
      # Record previous state
      Previous_State=1
    elif Current_State==0 and Previous_State==1:
      # PIR has returned to ready state
      print ("Ready")
      Previous_State=0
 
    # Wait for 10 milliseconds
    time.sleep(0.01)
 
except KeyboardInterrupt:
  print ("Quit")
  # Reset GPIO settings
  GPIO.cleanup()
