import RPi.GPIO as GPIO
import time
import random
from mqtt import MQTTWrapper

class SoundPanic:
    INTERVALS = {
        "0-3": 2000,
        "3-6": 1500,
        "6-9": 1000,
        "9-12": 600,
        "12-15": 400
    }
    
    def __init__(self, trig, echo, ledcontroller, buzzercontroller):
        self.TRIG = trig
        self.ECHO = echo
        self.led = ledcontroller
        self.buzzer = buzzercontroller
        
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        
        self.mqtt = MQTTWrapper()
    
    def measure_distance(self):
        GPIO.output(self.TRIG, False)
        time.sleep(0.05)

        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        timeout = time.time() + 0.02
        while GPIO.input(self.ECHO) == 0 and time.time() < timeout:
            pulse_start = time.time()

        timeout = time.time() + 0.02
        while GPIO.input(self.ECHO) == 1 and time.time() < timeout:
            pulse_end = time.time()

        if 'pulse_start' not in locals() or 'pulse_end' not in locals():
            return None

        return round((pulse_end - pulse_start) * 17150, 2)
    
    def quantify_distance(self, d):
        if d is None:
            return None
        elif 0 <= d < 3:
            return "0-3"
        elif 3 <= d < 6:
            return "3-6"
        elif 6 <= d < 9:
            return "6-9"
        elif 9 <= d < 12:
            return "9-12"
        elif 12 <= d < 15:
            return "12-15"
        else:
            return None
    
    def start(self):
        self.mqtt.start()
        self.led.set_red(True)
        self.led.set_green(False)
        
        #self.mqtt.wait_for_start()
        self.led.set_red(False)
        self.led.set_green(True)
        
        last_blink = time.time()
        rounds = 0
        
        while rounds < 3 and not self.mqtt.stop_event.is_set():
            if self.mqtt.stop_event.is_set():
                print("Game ended by server")
                break
            
            self.led.set_yellow(True)
            target_interval = random.choice(list(self.INTERVALS.keys()))
            target_freq = self.INTERVALS[target_interval]
            
            self.buzzer.play(target_freq)
            time.sleep(5)
            self.buzzer.stop()

            start_time = None
            validated = False

            while not validated and not self.mqtt.stop_event.is_set():
                    
                if time.time() - last_blink >= 0.4:
                    self.led.toggle_green()
                    last_blink = time.time()
                
                self.led.toggle_yellow()

                d = self.measure_distance()
                interval = self.quantify_distance(d)

                if interval in self.INTERVALS:
                    freq = self.INTERVALS[interval]
                    self.buzzer.play(freq)
                else:
                    self.buzzer.stop()

                if interval == target_interval:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 5:
                        print("OK")
                        validated = True
                        self.buzzer.stop()
                        self.led.set_yellow(True)
                else:
                    start_time = None

                time.sleep(0.5)

            time.sleep(2)
            rounds += 1

        if self.mqtt.stop_event.is_set():
            print("Game ended by server")
        else:
            print("Finished")
            self.mqtt.publish_state("SUCCESS")
            while time.time() - last_blink >= 0.4:
                self.led.toggle_green()
                last_blink = time.time()
            
        self.led.reset()
        self.buzzer.cleanup()