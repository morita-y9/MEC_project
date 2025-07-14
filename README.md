# coding: UTF-8
import RPi.GPIO as GPIO
from display import display
import threading
import time
from datetime import datetime
import serial
import queue

# --- 初期設定 ---
ser = serial.Serial('/dev/rfcomm0', 9600)
print("Waiting for request...")

# GPIOピン設定
LED1 = 17
LED2 = 27
LED3 = 22
SW1 = 24
SW2 = 21
pwmpin = 23
bkled = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)
GPIO.setup(pwmpin, GPIO.OUT)
pin23 = GPIO.PWM(pwmpin, 10)
GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bkled, GPIO.OUT)
GPIO.output(bkled, True)

fault_mode = False
LCD = display()

# 通信用キュー
tx_queue = queue.Queue()

# --- safe_sleep ---
def safe_sleep(duration, check_interval=0.1):
    elapsed = 0
    while elapsed < duration:
        if fault_mode:
            break
        time.sleep(check_interval)
        elapsed += check_interval

# --- シリアル通信管理スレッド ---
def serial_manager():
    global fault_mode
    while True:
        try:
            # 通信要求がある場合
            if not tx_queue.empty():
                msg = tx_queue.get()
                ser.write(msg.encode('utf-8'))
                print(f"送信: {msg.strip()}")

                # ACK待ち
                ack = ser.readline().decode('utf-8').strip()
                print(f"ACK受信: {ack}")

                if ack == 'ACK':
                    now = datetime.now()
                    timestamp = now.strftime('%Y%m%d%H%M')
                    data = f"U:6600,OK, V:0, NG, W:6620, OK, {timestamp}, END"
                    ser.write(data.encode('utf-8'))
                    print(f"異常データ送信: {data}")
            else:
                # 通常時にホストからのリクエストを受信
                if not fault_mode:
                    line = ser.readline().decode('utf-8').strip()
                    if line == 'REQHPCRP1':
                        print(f"ホストから受信: {line}")
                        ser.write(b"U:6600,OK, V:6610,OK, W:6620,OK, END\n")
                        print("正常データ送信完了")
        except Exception as e:
            print(f"通信エラー: {e}")
            time.sleep(0.1)

# 起動
threading.Thread(target=serial_manager, daemon=True).start()

# --- 異常系処理 ---
def fault_handler():
    global fault_mode
    fault_mode = True

    # pin23.start(50)
    # pin23.ChangeFrequency(600)

    # 通信要求をキューに追加
    tx_queue.put('REQHPCRP1\n')
    print("異常時リクエスト送信要求")

    # LCDやLEDを表示
    while GPIO.input(SW1) == GPIO.HIGH and GPIO.input(SW2) == GPIO.LOW:
        if GPIO.input(SW2) != GPIO.LOW:
            break

        GPIO.output(LED1, 1)
        GPIO.output(LED2, 0)
        GPIO.output(LED3, 1)

        LCD.clear()
        LCD.put('Trouble')
        LCD.pos(1, 0)
        LCD.put('Fault:V')
        safe_sleep(1)

    fault_mode = False
    LCD.clear()
    pin23.stop()
    print("異常モード終了")

# --- 割り込み設定 ---
def callback(channel):
    if not fault_mode:
        threading.Thread(target=fault_handler, daemon=True).start()

GPIO.add_event_detect(SW2, GPIO.FALLING, callback=callback, bouncetime=200)

# --- 正常系処理 ---
try:
    while True:
        if not fault_mode and GPIO.input(SW1) == GPIO.HIGH:
            pin23.stop()
            GPIO.output(LED1, 1)
            GPIO.output(LED2, 1)
            GPIO.output(LED3, 1)

            LCD.clear()
            LCD.put('U:6600V')
            LCD.pos(1, 0)
            LCD.put('Charging')
            safe_sleep(2)

            if fault_mode: continue

            LCD.clear()
            LCD.put('V:6610V')
            LCD.pos(1, 0)
            LCD.put('Charging')
            safe_sleep(2)

            if fault_mode: continue

            LCD.clear()
            LCD.put('W:6620V')
            LCD.pos(1, 0)
            LCD.put('Charging')
            safe_sleep(2)

            LCD.clear()
        else:
            if not fault_mode:
                GPIO.output(LED1, 0)
                GPIO.output(LED2, 0)
                GPIO.output(LED3, 0)

except KeyboardInterrupt:
    GPIO.cleanup()
    LCD.clear()
