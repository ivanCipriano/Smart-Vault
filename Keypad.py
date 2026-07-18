from machine import Pin
import time, ujson, _thread

class Keypad:
    # Costruttore della classe KeyPad, inizializza il tastierino
    def __init__(self, rPins, cPins, opening_pin, oled):
        
        # Definizione della matrice di tasti
        self.keyMatrix = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]
        
        # Definizione dei pin per le righe e le colonne della tastiera
        self.rowPins = rPins  # Pin per le righe
        
        self.colPins = cPins  # Pin per le colonne
        
        # Inizializzazione delle liste per i pin GPIO
        
        self.row = []  # Lista per i pin delle righe (output)
        
        self.column = []  # Lista per i pin delle colonne (input)
        
        # Configurazione dei pin GPIO
        for item in rPins:
            self.row.append(Pin(item, Pin.OUT))  # Imposta i pin delle righe come output
        for item in cPins:
            self.column.append(Pin(item, Pin.IN, Pin.PULL_DOWN))  # Imposta i pin delle colonne come input con pull-down

        self.opening_pin = opening_pin
        self.oled = oled
        self.count = 0
        self.alarm_sounds = False
        self.alarm_is_ringing = False
        self.open_door = False
        self.active_alarm = True
        self.thief = False
        self.restart = False
        self.change_pin = "####"
        
    # Metodo per scansionare la tastiera e rilevare i tasti premuti
    def scanKeypad(self):
        key_pressed = None
        for rowKey in range(4):  # Ciclo attraverso le righe della tastiera
            self.row[rowKey].value(1)  # Imposta il valore alto sulla riga corrente
            for colKey in range(4):  # Ciclo attraverso le colonne della tastiera
                if self.column[colKey].value() == 1:  # Se il valore della colonna è alto
                    key_pressed = self.keyMatrix[rowKey][colKey]  # Memorizza il tasto premuto
                    break  # Esci dal ciclo delle colonne
            self.row[rowKey].value(0)  # Ripristina il valore basso sulla riga
            if key_pressed is not None:
                break  # Esci dal ciclo delle righe se è stato trovato un tasto premuto
        return key_pressed

    # Metodo di verifica del pin di apertura
    def check_code(self):
        entered_pin = ""  # La stringa che contiene il pin inserito dall'utente è vuota
        last_key_pressed = None
        self.oled.fill(0)
        self.oled.text_fill("DIGITA CODICE:", 5, 10)
        x = 45
        y = 20

        while len(entered_pin) < 4:  # Rimane in questo ciclo fino a che l'utente non ha inserito un pin di 4 cifre
            pressed = self.scanKeypad()  # Assegno alla variabile "pressed" il valore di ritorno della scanKeypad()
            
            if pressed != None and pressed != last_key_pressed:  # Se l'utente ha premuto un tasto, aggiungo il numero premuto alla stringa
                entered_pin += pressed
                self.oled.text_no_fill("*", x, y)
                
                # Aggiorno la variabile x per la stampa degli asterischi a schermo
                x += 10
                last_key_pressed = pressed
                time.sleep(0.3)
            
            # Se è stato rilevato un ladro e l'allarme non sta suonando
            elif self.thief and not self.alarm_is_ringing:
                entered_pin = ""  # Resetta il pin inserito
                self.msg_thief()  # Mostra un messaggio di avviso del ladro
                self.oled.text_fill("DIGITA CODICE:", 5, 10)  # Mostra il messaggio per digitare il codice
                x = 45
                y = 20
            
            # Se è stato richiesto un riavvio
            elif self.restart:
                return  # Esce dal metodo
        
            # Se non è stato premuto alcun tasto
            elif pressed is None:    
                last_key_pressed = None  # Resetta l'ultimo tasto premuto
                
            time.sleep_ms(100)
        
        # Esco dal ciclo quando la dimensione è 4
        if entered_pin == self.opening_pin:  # Verifico se il codice inserito dall'utente è quello di apertura
            self.count = 0  # Imposto il conteggio pin errati a 0
            entered_pin = ""  # Imposto nuovamente il pin inserito a vuoto
            
            if not self.alarm_is_ringing and not self.open_door:  # Se l'allarme non era attivo, apro la porta
                self.active_alarm = False
                self.msg_open_door()
                
            elif not self.alarm_is_ringing and self.open_door:
                self.msg_close_door()
                self.active_alarm = True
            
            else:  # Altrimenti disattivo l'allarme
                self.alarm_sounds = False  # Disattivo il suono dell'allarme
                self.alarm_is_ringing = False  # L'allarme non è più attivo
                self.thief = False
                self.msg_deact_alarm()
                
        # Se il pin inserito corrisponde al pin di cambio e la porta non è aperta
        elif entered_pin == self.change_pin and not self.open_door and not self.alarm_is_ringing:
            entered_pin = ""  # Resetta il pin inserito
            count = 0  # Resetta il conteggio degli errori
            self.insert_new_pin()  # Avvia la procedura per inserire un nuovo pin

        else:
            self.count += 1  # Aumento il conteggio pin errati
            entered_pin = ""  # Imposto il pin inserito a vuoto
            self.msg_wrong_code()

            # Verifico se il codice è stato inserito in maniera errata due volte
            if self.count == 2 and not self.alarm_is_ringing and not self.open_door:  
                self.count = 0  # Resetto il conteggio
                self.msg_active_alarm()
                entered_pin = ""  # Imposto il pin inserito a vuoto


    def insert_new_pin(self):
        self.count = 0
        entered_pin = ""
        last_key_pressed = None
        self.msg_change_pin()
        x = 45
        y = 30
        
        # Rimane in questo ciclo fino a che l'utente non ha inserito un pin di 4 cifre
        while len(entered_pin) < 4:
            
            # Assegno alla variabile "pressed" il valore di ritorno della scanKeypad()
            pressed = self.scanKeypad()  
            
            # Se l'utente ha premuto un tasto, aggiungo il numero premuto alla stringa
            if pressed != None and pressed != last_key_pressed:  
                entered_pin += pressed
                self.oled.text_no_fill("*", x, y)
                
                # Aggiorno la variabile x per la stampa degli asterischi a schermo
                x += 10
                last_key_pressed = pressed
                time.sleep(0.3)
            
            # Se non è stato premuto alcun tasto, resetto l'ultimo tasto premuto
            elif pressed is None:
                last_key_pressed = None
            
            time.sleep_ms(100)
        
        # Se il pin inserito corrisponde al pin di apertura
        if entered_pin == self.opening_pin:
            entered_pin = ""
            self.msg_set_new_pin()
            x = 45
            y = 30
            last_key_pressed = None
            
            # Rimane in questo ciclo fino a che l'utente non ha inserito un nuovo pin di 4 cifre
            while len(entered_pin) < 4:
                
                # Assegno alla variabile "pressed" il valore di ritorno della scanKeypad()
                pressed = self.scanKeypad()  
                
                # Se l'utente ha premuto un tasto, aggiungo il numero premuto alla stringa
                if pressed != None and pressed != last_key_pressed: 
                    entered_pin += pressed
                    self.oled.text_no_fill("*", x, y)
                    
                    # Aggiorno la variabile x per la stampa degli asterischi a schermo
                    x += 10
                    last_key_pressed = pressed
                    time.sleep(0.3)
                
                # Se non è stato premuto alcun tasto, resetto l'ultimo tasto premuto
                elif pressed is None:
                    last_key_pressed = None
                
                time.sleep_ms(100)
            
            #se il nuovo pin inserti è uguale alla combinazione di cambio pin, allora
            # il cambio non viene concesso
            if entered_pin == self.change_pin:
                self.oled.text_fill("COMBINAZIONE",15,10)
                self.oled.text_no_fill("NON CONCESSA",15,20)
                time.sleep(2)
            
            else:
                # Imposto il nuovo pin di apertura
                self.opening_pin = entered_pin
                entered_pin = ""
                self.oled.text_fill("CAMBIO PIN", 25, 10)
                self.oled.text_no_fill("EFFETTUATO", 25, 25)
                time.sleep(1)
        
        # Se il pin inserito non corrisponde al pin di apertura
        else:
            self.oled.text_fill("CODICE ERRATO!", 5, 10)
            time.sleep(1)
            self.oled.text_fill("CAMBIO PIN", 25, 10)
            self.oled.text_no_fill("NON CONCESSO", 15, 20)
            entered_pin = ""
            time.sleep(1.5)
        
    
    # Metodo per leggere l'input da tastierino
    def read_input(self):
        while True:
            self.check_code()
            # Se viene richiesto un riavvio, esce dal ciclo
            if self.restart:
                break
        self.restart = False
        self.oled.fill(0)
        #esce da questo thread
        _thread.exit()
    
    # Metodo per stampare messaggio di apertura porta su oled
    def msg_open_door(self):
        self.oled.text_fill("CODICE ESATTO", 5, 10)
        time.sleep(1.5)
        self.open_door = True
        self.oled.text_fill("APERTURA PORTA", 5, 10)
        time.sleep(1.5)
    
    # Metodo per stampare messaggio di chiusura porta su oled
    def msg_close_door(self):
        self.oled.text_fill("CODICE ESATTO", 5, 10)
        time.sleep(1.5)
        self.open_door = False
        self.oled.text_fill("CHIUSURA PORTA", 5, 10)
        time.sleep(1.5)
    
    # Metodo per stampare messaggio di disattivazione allarme
    def msg_deact_alarm(self):
        self.oled.text_fill("ALLARME", 35, 10)
        self.oled.text_no_fill("DISATTIVATO", 18, 20)
        time.sleep(1)
    
    # Metodo per stampare messaggio codice errato
    def msg_wrong_code(self):
        self.oled.text_fill("CODICE ERRATO!", 5, 10)
        time.sleep(1.5)
    
    # Metodo per stampare messaggio attivazione allarme
    def msg_active_alarm(self):
        self.oled.text_fill("CAVEAUX", 40, 10)
        self.oled.text_no_fill("BLOCCATO", 35, 20)
        time.sleep(1.5)
        self.oled.text_fill("ALLARME CAVEAU", 5, 10)
        for i in range(5, 0, -1):
            count_down = "00:0" + str(i)
            self.oled.text_no_fill(count_down, 45, 20)
            time.sleep(1)
            self.oled.fill_rect(78, 20, 79, 20, 0)
        self.alarm_sounds = True  # Suona l'allarme
        self.alarm_is_ringing = True
        self.oled.text_fill("ALLARME ATTIVO", 5, 10)
        time.sleep(3)
    
    # Metodo per stampare messaggio di avviso del ladro
    def msg_thief(self):
        self.alarm_sounds = True  # Suona l'allarme
        self.oled.text_fill("ALLARME ATTIVO", 5, 10)
        time.sleep(3)
    
    # Metodo per stampare messaggio di cambio pin
    def msg_change_pin(self):
        self.oled.text_fill("CAMBIO CODICE", 5, 10)
        time.sleep(2)
        self.oled.text_fill("INSERISCI IL", 5, 10)
        self.oled.text_no_fill("VECCHIO CODICE:", 5, 20)
    
    # Metodo per stampare messaggio di inserimento nuovo pin
    def msg_set_new_pin(self):
        self.oled.text_fill("CODICE ESATTO", 5, 10)
        time.sleep(1)
        self.oled.text_fill("INSERISCI IL", 15, 10)
        self.oled.text_no_fill("NUOVO CODICE:", 15, 20)
    
    # Metodo per ottenere lo stato dell'allarme in formato JSON
    def get_ujson_active_alarm(self):
        if self.active_alarm:
            return ujson.dumps({"allarme_attivo": "ON"})
        else:
            return ujson.dumps({"allarme_attivo": "OFF"})
    
    # Metodo per impostare lo stato del suono dell'allarme
    def set_alarm_sounds(self, sounds):
        self.alarm_sounds = sounds
    
    # Metodo per ottenere lo stato del suono dell'allarme
    def get_alarm_sounds(self):
        return self.alarm_sounds
    
    # Metodo per impostare il conteggio degli errori
    def set_count(self, count):
        self.count = count
    
    # Metodo per impostare lo stato di "allarme che sta suonando"
    def set_alarm_is_ringing(self, state):
        self.alarm_is_ringing = state
    
    # Metodo per ottenere lo stato di "allarme che sta suonando"
    def get_alarm_is_ringing(self):
        return self.alarm_is_ringing
    
    # Metodo per ottenere lo stato di "allarme che sta suonando" in formato JSON
    def get_ujson_alarm_is_ringing(self):
        return ujson.dumps({"allarme_sta_suonando": self.alarm_is_ringing})
    
    # Metodo per impostare lo stato di apertura della porta
    def set_open_door(self, door_state):
        self.open_door = door_state
    
    # Metodo per ottenere lo stato di apertura della porta
    def get_open_door(self):
        return self.open_door
    
    # Metodo per impostare lo stato di attivazione dell'allarme
    def set_active_alarm(self, state):
        self.active_alarm = state
    
    # Metodo per ottenere lo stato di attivazione dell'allarme
    def get_active_alarm(self):
        return self.active_alarm
    
    # Metodo per ottenere il pin di apertura
    def get_opening_pin(self):
        return self.opening_pin
    
    # Metodo per impostare lo stato di "ladro rilevato"
    def set_thief(self, thief):
        self.thief = thief
    
    # Metodo per ottenere lo stato di "ladro rilevato"
    def get_thief(self):
        return self.thief
    
    # Metodo per impostare lo stato di riavvio
    def set_restart(self, restart):
        self.restart = restart