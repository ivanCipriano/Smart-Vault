from Keypad import Keypad  
from Alarm import Alarm  
from Door import Door  
from mqtt import MQTT  
from Display import Display  
from machine import PWM, Pin, I2C  
import time, _thread, ssd1306, network, ujson, json  
from Sensor_HW import Sensor_HW  

#Parametri di configurazione MQTT
MQTT_CLIENT_ID = "gruppo04"  #ID del client MQTT
MQTT_BROKER = "test.mosquitto.org"  #Indirizzo del broker MQTT
MQTT_USER = ""  #Nome utente per l'autenticazione MQTT (vuoto in questo caso)
MQTT_PASSWORD = ""  #Password per l'autenticazione MQTT (vuota in questo caso)

#Topic MQTT su cui il sistema pubblica
MQTT_MANUAL_SYSTEM = "FortiVault/System/Manual/State"  #Topic per lo stato del sistema manuale
MQTT_ALARM_STATE = "FortiVault/Alarm/State"  #Topic per lo stato dell'allarme
MQTT_NOTIFICATION = "FortiVault/Alarm/Notification"  #Topic per le notifiche dell'allarme
MQTT_DOOR_STATE = "FortiVault/Door/State"  #Topic per lo stato della porta
MQTT_LIGHTS_STATE = "FortiVault/Lights/State"  #Topic per lo stato delle luci
MQTT_DAILY_ACCESS = "FortiVault/Door/Access"  #Topic per gli accessi giornalieri

#Topic MQTT a cui il sistema è iscritto
MQTT_SUBSCRIBE_TOPIC = {  #Dizionario dei topic a cui il sistema si iscrive
    "MQTT_SYSTEM_RESET": b'FortiVault/System/State',  #Topic per il reset del sistema
    "MQTT_MANUAL_SYSTEM": b'FortiVault/System/Manual',  #Topic per il sistema manuale
    "MQTT_MANUAL_DOOR": b'FortiVault/System/Manual/Door',  #Topic per la porta manuale
    "MQTT_MANUAL_ALARM": b'FortiVault/System/Manual/Alarm'  #Topic per l'allarme manuale
}

#Dizionari per gestire i valori dei sensori e degli attuatori e il loro stato
#Valori da pubblicare sui topic
MQTT_PUBLISH_VALUE = {  
    MQTT_MANUAL_SYSTEM: None,
    MQTT_ALARM_STATE : None,
    MQTT_NOTIFICATION : None,
    MQTT_DOOR_STATE : None,
    MQTT_LIGHTS_STATE : None,
    MQTT_DAILY_ACCESS : None
}

#Valori attuali rilevati dai sensori
MQTT_ACTUAL_VALUE = {  
    MQTT_MANUAL_SYSTEM: 'false',
    MQTT_ALARM_STATE : None,
    MQTT_NOTIFICATION : None,
    MQTT_DOOR_STATE : None,
    MQTT_LIGHTS_STATE : None,
    MQTT_DAILY_ACCESS : None
}

#Parametri di sistema
SYSTEM_PARAMS = {  
    "BOOT": True,
    "RESTART_SYSTEM": False,
    "MANUAL_SYSTEM" : False,
    "MANUAL_DOOR" : False,
    "MANUAL_ALARM" : False
}

#Parametri del Display
WIDTH = 128
HEIGHT = 64

#Pin display per keypad
SCL_PIN_KP = 16
SDA_PIN_KP = 21
SERIAL_OLED_KP = 0

#Pin per il buzzer
PIN_BUZZER = 26

#Pin per i led dell'allarme
PIN_BUZZ_LEDS = [25,27]

#Pin per le righe e le colonne del tastierino
ROWPINS = [19,18,5,17]
COLPINS = [4,2,12,13]

#Codice di apertura della porta
OPENING_PIN = "1206"

#Pin per la porta
PIN_DOOR = 32

#Pin lampadina
PIN_LUX = 22

#Definisco i pin del display per il monitoraggio dello stato
SCL_PIN_OLED_STATE = 15
SDA_PIN_OLED_STATE = 0
SERIAL_OLED_STATE = 1

#Pin per il sensore di movimento
SENSOR_PIN = 14

#Creazione istanze oggetti
# Crea un oggetto Display per il pannello OLED collegato al tastierino.
oledKp = Display(SERIAL_OLED_KP, WIDTH, HEIGHT, SCL_PIN_KP, SDA_PIN_KP)

# Crea un oggetto Keypad per il tastierino. 
keypad = Keypad(ROWPINS, COLPINS, OPENING_PIN, oledKp)

# Crea una lista di oggetti PWM per i LED collegati all'allarme. 
# Ogni LED è configurato come output con un duty cycle iniziale di 0 (spento).
leds = [PWM(Pin(led,Pin.OUT),duty = 0) for led in PIN_BUZZ_LEDS]

# Crea un oggetto Alarm per l'allarme.
alarm = Alarm(leds,PIN_BUZZER)

# Crea un oggetto Door per la porta.
door = Door(PIN_DOOR)

# Imposta l'angolo del servo motore della porta a 112 gradi, che corrisponde alla posizione di chiusura.
door.set_angle(112)

# Crea un oggetto Sensor_HW per il sensore di movimento.
sensor = Sensor_HW(SENSOR_PIN)

# Configura un interrupt sul sensore di movimento. 
sensor.setup_interrupt()

# Crea un oggetto Display per il pannello OLED che mostra lo stato del sistema.
oled_state = Display(SERIAL_OLED_STATE, WIDTH, HEIGHT, SCL_PIN_OLED_STATE, SDA_PIN_OLED_STATE)

# Pulisce il display dello stato impostando tutti i pixel a 0 (nero).
oled_state.fill(0)

# Configura il pin del LED che simula la luce come output.
lux = Pin(PIN_LUX,Pin.OUT)

# Spegne il LED che simula la luce.
lux.off()

# Crea un oggetto MQTT per la comunicazione con il broker MQTT.
client = MQTT(MQTT_CLIENT_ID,MQTT_BROKER)

#Questa funzione tenta di connettersi alla rete WiFi e visualizza lo stato della
#connessione sul display
def wifi_connect():
    
    try:
        x = 0
        oled_state.text_fill("Connecting",0,10)
        oled_state.text_no_fill("to Wifi",0,20)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect('Redmi 12 Pro','12345678')
        while not sta_if.isconnected():
            oled_state.text_no_fill(".", 53+x ,20)
            time.sleep(0.1)
            x = x + 6
        oled_state.text_no_fill("Connected",0,30)
    except OSError as e:
        oled_state.text_no_fill("Not Connected!",0,30)
    
#Questa funzione si connette al broker MQTT, si iscrive ai topic e avvia un thread per
#leggere l'input del tastierino
def mqtt_connection():
    x = 0
    oled_state.text_fill("Connecting to", 0, 10)
    oled_state.text_no_fill("MQTT server", 0, 20)
    client.connect(MQTT_SUBSCRIBE_TOPIC, subCallback)
    while x < 28:
        
        oled_state.text_no_fill(".", x+85, 20)
        time.sleep(0.1)
        x = x + 6
    if client.get_conn_state():
        oled_state.text_no_fill("Connected!", 0, 30)
        oled_state.fill(0)
        
        # Avvio del thread secondario per la lettura dell'input
        _thread.start_new_thread(keypad.read_input, ())
    else:
        oled_state.text_no_fill("Not Connected!", 0, 30)
        oled_state.fill(0)
        raise OSException
    

#Questa funzione stampa lo stato fisso del sistema sul display
def print_state():
    oled_state.text_fill("Stato sistema", 0, 1)
    oled_state.text_no_fill("Mod:",1,10)
    oled_state.text_no_fill("Stato a.:",1,21)
    oled_state.circle_no_fill(112,24,4,1)
    oled_state.text_no_fill("Porta:",1,30)
    oled_state.text_no_fill("Luce:",1,40)
    oled_state.text_no_fill("N. accessi:",1,50)

#funzione di stampa dei parametri dello stato del sistema che variano durante l'esecuzione
#del programma
def print_parameters():
    if SYSTEM_PARAMS["MANUAL_SYSTEM"] == False:
        oled_state.fill_rect(38,10,127,10)
        oled_state.text_no_fill("automatica",38,10)
    else:
        oled_state.fill_rect(38,10,127,10)
        oled_state.text_no_fill("manuale",38,10)


    for k,v in MQTT_PUBLISH_VALUE.items():
        if v != None:
            if k == MQTT_ALARM_STATE:
                oled_state.fill_rect(72,21,35,9)
                oled_state.text_no_fill(str(json.loads(MQTT_PUBLISH_VALUE[MQTT_ALARM_STATE])["allarme_attivo"]),76,21)
                
                message = str(json.loads(MQTT_PUBLISH_VALUE[MQTT_NOTIFICATION])["allarme_sta_suonando"])
                if message == "False":
                    oled_state.circle_fill(112,24,3,0)

            elif k == MQTT_DOOR_STATE:
                oled_state.fill_rect(53,30,127,10)
                oled_state.text_no_fill(str(json.loads(MQTT_PUBLISH_VALUE[MQTT_DOOR_STATE])["porta"]),53,30)
            
            elif k == MQTT_LIGHTS_STATE:
                oled_state.fill_rect(45,40,127,10)
                oled_state.text_no_fill(str(json.loads(MQTT_PUBLISH_VALUE[MQTT_LIGHTS_STATE])["luce"]),45,40)
                
            elif k == MQTT_DAILY_ACCESS:
                oled_state.fill_rect(90,50,127,10)
                oled_state.text_no_fill(str(json.loads(MQTT_PUBLISH_VALUE[MQTT_DAILY_ACCESS])["n_accessi"]),90,50)

#Questa funzione disegna un cerchio pieno sul display 'oled_state' per indicare che
#l'allarme è sta suonando.
def print_alarm_ringing():
    oled_state.circle_fill(112,24,3,1)

# Metodo per ottenere lo stato della luce in formato JSON
def get_ujson_lux_state():
    if lux.value():
        return ujson.dumps({"luce": "ON"})
    else:
        return ujson.dumps({"luce": "OFF"})

#Questa funzione legge i valori attuali dai sensori e li memorizza nel
#dizionario MQTT_ACTUAL_VALUE
def read_sensors_value():
    
    global oled_state, alarm, keypad, door, MQTT_ACTUAL_VALUE
    global MQTT_NOTIFICATION, MQTT_ALARM_STATE, MQTT_DOOR_STATE, MQTT_DAILY_ACCESS, MQTT_LIGHTS_STATE
    MQTT_ACTUAL_VALUE[MQTT_ALARM_STATE] = keypad.get_ujson_active_alarm()
    MQTT_ACTUAL_VALUE[MQTT_NOTIFICATION] = keypad.get_ujson_alarm_is_ringing()
    MQTT_ACTUAL_VALUE[MQTT_DOOR_STATE] = door.get_ujson_door_state()
    MQTT_ACTUAL_VALUE[MQTT_LIGHTS_STATE] = get_ujson_lux_state()
    MQTT_ACTUAL_VALUE[MQTT_DAILY_ACCESS] = door.get_ujson_n_access()
    
#Questa funzione viene richiamata quando arriva un nuovo messaggio MQTT; aggiorna le
#variabili di stato in base al messaggio
def subCallback(topic, msg):
    
    if topic == MQTT_SUBSCRIBE_TOPIC["MQTT_SYSTEM_RESET"]:
        if msg == b'true':
            SYSTEM_PARAMS["RESTART_SYSTEM"] = True
        elif msg == b'false':
            SYSTEM_PARAMS["RESTART_SYSTEM"] = False
    if topic == MQTT_SUBSCRIBE_TOPIC["MQTT_MANUAL_SYSTEM"]:
        if msg == b'true':
            SYSTEM_PARAMS["MANUAL_SYSTEM"] = True
        elif msg == b'false':
            SYSTEM_PARAMS["MANUAL_SYSTEM"] = False
    
    if topic == MQTT_SUBSCRIBE_TOPIC["MQTT_MANUAL_DOOR"]:
        if msg == b'true':
            SYSTEM_PARAMS["MANUAL_DOOR"] = True
            manual_door_open()
        elif msg == b'false':
            SYSTEM_PARAMS["MANUAL_DOOR"] = False
            manual_door_close()
    
    if topic == MQTT_SUBSCRIBE_TOPIC["MQTT_MANUAL_ALARM"]:
        if msg == b'true':
            SYSTEM_PARAMS["MANUAL_ALARM"] = True
            manual_alarm_deact()
        elif msg == b'false':
            SYSTEM_PARAMS["MANUAL_ALARM"] = False
            manual_alarm_active()

#Questa funzione apre la porta, accende la luce, disattiva l'allarme e aggiorna il
#sensore della porta
def manual_door_open():
    lux.on()
    door.set_angle(22)
    keypad.set_open_door(True)
    keypad.set_active_alarm(False)
    sensor.set_door_sensor(True)

#Questa funzione chiude la porta, spegne la luce, attiva l'allarme (se non in modalità manuale)
#e aggiorna il sensore della porta
def manual_door_close():
    lux.off()
    door.set_angle(112)
    keypad.set_open_door(False)
    if not SYSTEM_PARAMS["MANUAL_ALARM"]:
        keypad.set_active_alarm(True)
        sensor.set_door_sensor(False)

#Questa funzione chiude la porta, spegne la luce, attiva l'allarme (se non in modalità manuale)
#e aggiorna il sensore della porta
def manual_alarm_deact():
    keypad.set_active_alarm(False)
    sensor.set_door_sensor(True)

#Questa funzione attiva l'allarme e aggiorna il sensore dell'allarme
def manual_alarm_active():
    keypad.set_active_alarm(True)
    sensor.set_door_sensor(False)

#Questa funzione riavvia il sistema, reimpostando tutti i parametri di sistema e i valori dei
#sensori
def restart_procedure():
    
    global MQTT_PUBLISH_VALUE,MQTT_ACTUAL_VALUE,SYSTEM_PARAMS
    global oledKp,keypad,leds,alarm,door,oled_state,lux,sensor

    keypad.set_restart(True)
    keypad.set_alarm_sounds(False)
    keypad.set_alarm_is_ringing(False)
    keypad.set_active_alarm(True)
    keypad.set_open_door(False)
    keypad.set_thief(False)
    keypad.set_count(0)
    alarm.alarm_stop()
    door.set_angle(112)
    lux.off()
    oled_state.text_fill("Restarting the",1,1)
    oled_state.text_no_fill("system",1,10)
    sensor.set_alarm_sensor(False)
    sensor.set_door_sensor(False)
    sensor.set_thief_sensor(False)


    MQTT_PUBLISH_VALUE = {
        MQTT_MANUAL_SYSTEM: None,
        MQTT_ALARM_STATE : None,
        MQTT_NOTIFICATION : None,
        MQTT_DOOR_STATE : None,
        MQTT_LIGHTS_STATE : None,
        MQTT_DAILY_ACCESS : None
    }

    MQTT_ACTUAL_VALUE = {
        MQTT_MANUAL_SYSTEM: 'false',
        MQTT_ALARM_STATE : None,
        MQTT_NOTIFICATION : None,
        MQTT_DOOR_STATE : None,
        MQTT_LIGHTS_STATE : None,
        MQTT_DAILY_ACCESS : None
    }
    
    MQTT_PUBLISH_VALUE = client.publish_new_value(MQTT_PUBLISH_VALUE,MQTT_ACTUAL_VALUE)
    

    SYSTEM_PARAMS = {
        "BOOT": True,
        "RESTART_SYSTEM": False,
        "MANUAL_SYSTEM" : False,
        "MANUAL_DOOR" : False,
        "MANUAL_ALARM" : False
    }

#Loop principale
# Questo ciclo continua a leggere i valori dei sensori, a pubblicare i valori sui topic MQTT,
#a controllare i messaggi MQTT in arrivo e a gestire l'allarme e la porta in base ai valori
#dei sensori
while True: 
    
    if SYSTEM_PARAMS["BOOT"] == True:
        wifi_connect()  #Connettiti alla rete WiFi
        mqtt_connection()  #Connettiti al broker MQTT
        print_state()  #Stampa lo stato iniziale del sistema
        #Pubblica i valori attuali sui topic MQTT
        MQTT_PUBLISH_VALUE = client.publish_new_value(MQTT_PUBLISH_VALUE, MQTT_ACTUAL_VALUE)
        SYSTEM_PARAMS["BOOT"] = False  #Imposta BOOT a False, indicando che il sistema ha completato l'avvio

    #Se il sistema non è in fase di riavvio (RESTART_SYSTEM == False)
    if SYSTEM_PARAMS["RESTART_SYSTEM"] == False:
        try:
            read_sensors_value()  #Legge i valori attuali dai sensori
        except OSError as e:
            print("Errore mentre leggo i valori del sensore", e)

        try:
            #Pubblica i valori attuali sui topic MQTT e aggiorna i parametri visualizzati  
            MQTT_PUBLISH_VALUE = client.publish_new_value(MQTT_PUBLISH_VALUE,MQTT_ACTUAL_VALUE)
            print_parameters()
        except OSError as e:
            print("Errore durante la pubblicazione dei dati", e)

        try:
            client.check_msg()  #Controlla se ci sono nuovi messaggi MQTT
        except OSError as e:
            print("Il check dei messaggi dal broker ha fallito", e)

        #Se l'allarme sta suonando
        while keypad.get_alarm_sounds():
            keypad.set_alarm_is_ringing(True)  #Imposta l'allarme come suonante
            MQTT_ACTUAL_VALUE[MQTT_NOTIFICATION] = keypad.get_ujson_alarm_is_ringing()  #Aggiorna il valore dell'allarme
            MQTT_PUBLISH_VALUE = client.publish_new_value(MQTT_PUBLISH_VALUE,MQTT_ACTUAL_VALUE)  #Pubblica il nuovo stato dell'allarme
            print_alarm_ringing()  #Stampa sul display il fatto che l'allarme sta suonando
            sensor.set_alarm_sensor(True)  #Imposta il sensore dell'allarme come attivo
            alarm.alarm_sound()  #Fai suonare l'allarme

        #Se l'allarme è attivo e non sta suonando
        if alarm.get_alarm_status() and not keypad.get_alarm_is_ringing():
            alarm.alarm_stop()  #Ferma l'allarme
            sensor.set_alarm_sensor(False)  #Imposta il sensore dell'allarme come inattivo

        #Se il sensore di movimento rileva un movimento e la porta è chiusa
        elif sensor.get_thief_sensor() and not keypad.get_open_door():
            keypad.set_thief(True)  #Imposta il sistema come in stato di furto
            sensor.set_alarm_sensor(True)  #Imposta il sensore dell'allarme come attivo
            sensor.set_thief_sensor(False)  #Resetta il sensore di movimento

        #Se la porta è aperta e lo stato della porta è chiusa
        elif keypad.get_open_door() and not door.get_door_state():
            door.set_angle(22)  #Apri la porta
            lux.on()  #Accendi la luce
            sensor.set_door_sensor(True)  #Imposta il sensore della porta come aperta

        #Se la porta è chiusa e lo stato della porta è aperta
        elif not keypad.get_open_door() and door.get_door_state():
            door.set_angle(112)  #Chiudi la porta
            lux.off()  #Spegni la luce
            sensor.set_door_sensor(False)  #Imposta il sensore della porta come chiusa

    #Se il sistema è in fase di riavvio (RESTART_SYSTEM == True)
    else:
        restart_procedure()  #Avvia la procedura di riavvio del sistema

    time.sleep_ms(1)

