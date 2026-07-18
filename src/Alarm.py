from machine import PWM, Pin
import time,math,ujson

class Alarm:
    # Il costruttore della classe inizializza il buzzer e altre variabili di istanza
    def __init__(self, leds, pin_buzzer):
        self.__PI = 3.14  # Costante PI utilizzata per calcoli matematici
        self.leds = leds  # Riferimento agli oggetti LED
        self.buzzer = PWM(Pin(pin_buzzer, Pin.OUT), freq=1, duty=512)  # Inizializza il buzzer
        self.alarm_is_ringing = False  # Stato iniziale dell'allarme

    # Metodo per simulare il suono sinusoidale dell'allarme
    def alarm_sound(self):
        self.alarm_is_ringing = True  # Imposta lo stato dell'allarme come attivo
        self.buzzer.init()  # Inizializza il buzzer
        for x in range(0, 36):  # Ciclo per generare il suono sinusoidale
            sinVal = math.sin(x * 10 * self.__PI / 180)  # Calcola il valore sinusoidale
            toneVal = 2000 + int(sinVal * 500)  # Calcola la frequenza del tono
            self.buzzer.freq(toneVal)  # Imposta la frequenza del buzzer
            time.sleep_ms(10)  # Pausa di 10 millisecondi
            # Modifica dell'intensità dei LED utilizzando la stessa funzione sinusoidale
            brightness = int((math.sin(x * self.__PI / 180) + 1) * 50)  # Calcola la luminosità dei LED
            for led in self.leds:
                led.duty(brightness)  # Imposta la luminosità dei LED
        time.sleep_ms(10)  # Pausa aggiuntiva per rallentare il ciclo

    # Metodo per interrompere l'allarme
    def alarm_stop(self):
        self.alarm_is_ringing = False  # Imposta lo stato dell'allarme come inattivo
        self.buzzer.deinit()  # Disattiva il buzzer
        for led in self.leds:
            led.duty(0)  # Spegne i LED

    # Metodo per ottenere lo stato dell'allarme in formato JSON
    def get_ujson_alarm_status(self):
        message = ujson.dumps({"allarme_sta_suonando": self.alarm_is_ringing})
        return message

    # Metodo per impostare lo stato dell'allarme
    def set_alarm_status(self, state):
        self.alarm_is_ringing = state

    # Metodo per ottenere lo stato dell'allarme
    def get_alarm_status(self):
        return self.alarm_is_ringing
