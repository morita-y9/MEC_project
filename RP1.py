# coding: UTF-8
import RPi.GPIO as GPIO
from display import display
import threading
import time
from datetime import datetime
import serial

#bluetooth関連
ser = serial.Serial('/dev/rfcomm0',9600)
print("Waiting for request...")

    
#GPIOセットアップ
LED1 = 17                      
LED2 = 27                      
LED3 = 22                                                   
SW1 = 24
SW2 = 21
pwmpin = 23
bkled = 26
GPIO.setmode(GPIO.BCM)         
GPIO.setwarnings(False)        
GPIO.setup(LED1,GPIO.OUT)     
GPIO.setup(LED2,GPIO.OUT)      
GPIO.setup(LED3,GPIO.OUT)      
GPIO.setup(pwmpin,GPIO.OUT)  
pin23 = GPIO.PWM(pwmpin,10)
GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bkled,GPIO.OUT)
GPIO.output(bkled,True)

fault_mode = False
LCD = display()


#異常系(割り込み処理)
def fault_handler():
    global fault_mode
    fault_mode = True
    while GPIO.input(SW1) == GPIO.HIGH and GPIO.input(SW2) == GPIO.LOW:
        GPIO.output(LED1, 1)
        GPIO.output(LED2, 0)
        GPIO.output(LED3, 1)
        #LCD関連
        LCD.clear()
        LCD.put('Trouble')
        LCD.pos(1,0)
        LCD.put('Fault:V')
        time.sleep(1)
        #ブザー関連
        pin23.start(50)
        GPIO.output(pwmpin,GPIO.HIGH)
        pin23.ChangeFrequency(600)
        time.sleep(2)
        #異常時ホストPCにリクエストを送信する
        ser.write(b'REQHPCRP1\n')
        print("異常時リクエストを送信")
        
        #ACK待ち
        ack=ser.readline().decode('utf-8').strip()
        
        #タイムスタンプ
        now = datetime.now()
        timestamp=now.strftime('%Y%m%d%H%M')
        
        if ack =='ACK':
            print(f"ホストPCからACKを受信 {ack}")
            data = f"U:6600,OK, V:0, NG, W:6620, OK {timestamp}, END"
            ser.write(data.encode('utf-8'))
            print("ホストPCに異常時データを送信")
        
        time.sleep(1)
        
    fault_mode = False
    LCD.clear()

def callback(channel):
    if not fault_mode:
        threading.Thread(target=fault_handler, daemon=True).start()

GPIO.add_event_detect(SW2, GPIO.FALLING, callback=callback, bouncetime=200)


#正常系 
try:
    while True:
        if not fault_mode and GPIO.input(SW1) == GPIO.HIGH:
            pin23.stop()
            GPIO.output(LED1, 1)
            GPIO.output(LED2, 1)
            GPIO.output(LED3, 1)
            #正常時ホストPCからリクエストが来たときに正常時のデータを送信する
            line = ser.readline().decode('utf-8').strip()
            if line == "REQHPCRP1":
                print(f"受信:{line}")
                ser.write(b"U:6600,OK, V:6610, OK, W:6620, OK \n")
                print("送信完了")
            
            if fault_mode:
                continue
            LCD.clear()
            LCD.put('U:6600V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            if fault_mode:  
                continue
            LCD.clear()
            LCD.put('V:6610V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            if fault_mode:
                continue
            LCD.clear()
            LCD.put('W:6620V')
            LCD.pos(1,0)
            LCD.put('Charging')
            time.sleep(2)
            LCD.clear()
        else:
            if not fault_mode:
                GPIO.output(LED1, 0)
                GPIO.output(LED2, 0)
                GPIO.output(LED3, 0)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    LCD.clear()

