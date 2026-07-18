from machine import Pin

class Sensor_HW:
    # Inizializza l'oggetto Sensor_HW
    def __init__(self, sensor_pin):
        
        # Crea un oggetto Pin per il sensore con la modalità di input e pull-up
        self.sensor_HW = Pin(sensor_pin, Pin.IN, Pin.PULL_UP)
        
        # Inizializza le variabili di stato
        self.thief = False
        self.alarm_is_ringing = False
        self.open_door = False
    
    # Funzione di callback per l'interrupt del sensore
    def sensor_isr(self, pin):
        
        # Verifica se l'allarme non è attivo e la porta non è aperta
        if not self.alarm_is_ringing and not self.open_door:
        
            # Imposta lo stato del sensore in base al valore del pin
            if self.sensor_HW.value():
                self.thief = True
            else:
                self.thief = False
    
    # Configura l'interrupt per il sensore
    def setup_interrupt(self):
        # Imposta l'interrupt sul fronte di discesa e associa la funzione di callback
        self.sensor_HW.irq(trigger=Pin.IRQ_FALLING, handler=self.sensor_isr)
    
    # Imposta lo stato del sensore di intrusione
    def set_thief_sensor(self, thief):
        self.thief = thief
    
    # Ottiene lo stato del sensore di intrusione
    def get_thief_sensor(self):
        return self.thief
    
    # Imposta lo stato del sensore della porta
    def set_door_sensor(self, state):
        self.open_door = state
    
    # Ottiene lo stato del sensore della porta
    def get_door_sensor(self):
        return self.open_door
    
    # Imposta lo stato del sensore dell'allarme
    def set_alarm_sensor(self, alarm):
        self.alarm_is_ringing = alarm
    
    # Ottiene lo stato del sensore dell'allarme
    def get_alarm_sensor(self):
        return self.alarm_is_ringing