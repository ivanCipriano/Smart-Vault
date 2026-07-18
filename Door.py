from machine import Pin, PWM
import ujson

class Door:
    # Costruttore della classe
    def __init__(self, pin, freq=50):
        # Inizializza un oggetto PWM (Pulse Width Modulation) per controllare il servomotore
        self.door = PWM(Pin(pin), freq)  
        
        self.open_door = False  # Imposta lo stato iniziale della porta come chiusa
        self.n_access = 0  # Inizializza il contatore degli accessi a zero

    def set_angle(self, angle):
        duty_min = 26  # Valore minimo del duty cycle
        duty_max = 123  # Valore massimo del duty cycle
        
        # Calcola il duty cycle in base all'angolo desiderato
        duty = duty_min + (angle / 180) * (duty_max - duty_min)
        
        # Se l'angolo è 22 gradi, imposta la porta come aperta e incrementa il contatore degli accessi
        if angle == 22:
            self.open_door = True
            self.n_access += 1
        else:
            self.open_door = False
        
        # Imposta il duty cycle del servomotore
        self.door.duty(int(duty))
    
    # Restituisce il numero di accessi in formato JSON
    def get_ujson_n_access(self):
        return ujson.dumps({"n_accessi": self.n_access})
    
    # Imposta il numero di accessi
    def set_n_access(self, n_access):
        self.n_access = n_access

    # Imposta lo stato della porta (aperta o chiusa)    
    def set_door_state(self, state):
        self.open_door = state
    
    # Restituisce lo stato attuale della porta
    def get_door_state(self):
        return self.open_door

    # Restituisce lo stato della porta in formato JSON
    def get_ujson_door_state(self):
        if self.open_door:
            return ujson.dumps({"porta": "aperta"})
        else:
            return ujson.dumps({"porta": "chiusa"})