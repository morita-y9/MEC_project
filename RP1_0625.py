# coding: UTF-8
import RPi.GPIO as GPIO
from display import display
import time                    
                     
LED1 = 17                      
LED2 = 27                      
LED3 = 22
SW1 = 24
SW2 = 21
bkled = 26
GPIO.setmode(GPIO.BCM)         
GPIO.setwarnings(False)        
GPIO.setup(LED1,GPIO.OUT)     
GPIO.setup(LED2,GPIO.OUT)      
GPIO.setup(LED3,GPIO.OUT)      
GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(bkled,GPIO.OUT)
GPIO.output(bkled,True)



LCD = display()
try:
    while True:
    #正常系
        if GPIO.input(SW1) == GPIO.HIGH:
            GPIO.output(LED1, 1)
            GPIO.output(LED2, 1)
            GPIO.output(LED3, 1)
            LCD.clear()
            LCD.put('U:6600V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            LCD.clear()
            LCD.put('V:6610V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            LCD.clear()
            LCD.put('W:6620V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            LCD.clear()
        else:
            GPIO.output(LED1, 0)
            GPIO.output(LED2, 0)
            GPIO.output(LED3, 0)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    LCD.clear()

