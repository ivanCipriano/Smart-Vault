from umqtt.simple import MQTTClient

class MQTT:
    # Inizializza l'oggetto MQTT
    def __init__(self, client_id, broker_id, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}):
        # Crea un'istanza del client MQTT con i parametri specificati
        self.client = MQTTClient(client_id, broker_id, port=0, user=user, password=password, keepalive=keepalive, ssl=ssl, ssl_params=ssl_params)
        
        # Inizializza lo stato di connessione a False
        self.conn_state = False
    
    # Metodo per stabilire la connessione MQTT
    def connect(self, subs_topic_dict=dict(), sub_callback=None, qos=0):
        # Verifica se il valore di QoS è valido
        if qos > 2:
            print("Qos out of bound: min= 0, max= 2")
            self.conn_state = False
        
        # Verifica se la callback è fornita quando ci sono topic di sottoscrizione
        elif len(subs_topic_dict) > 0 and (not callable(sub_callback)):
            print("sub callback not callable")
            self.conn_state = False  
        
        # Stabilisce la connessione e sottoscrive ai topic specificati
        elif len(subs_topic_dict) > 0 and (callable(sub_callback)):
            self.client.connect()
            self.client.set_callback(sub_callback)
            for k, v in subs_topic_dict.items():
                self.client.subscribe(v, qos=qos)
            self.conn_state = True
    
    # Metodo per pubblicare nuovi valori sui topic
    def publish_new_value(self, pub=dict(), last_val=dict(), qos=0):
        
        # Verifica se ci sono valori da pubblicare
        if len(pub) > 0 and len(last_val) > 0:
            for k, v in last_val.items():
                
                # Pubblica il valore se è diverso dall'ultimo valore pubblicato
                if v != pub[k]:
                    pub[k] = v
                    self.client.publish(k, pub[k], qos=qos)
                    print(k, v)
            return pub
        return None
    
    # Metodo per sottoscrivere a un topic
    def subscribe(self, topic, qos=0):
        self.client.subscribe(topic, qos=qos)
    
    # Metodo per pubblicare un messaggio su un topic
    def publish(self, topic, msg, qos=0):
        self.client.publish(topic, msg, qos=qos)
    
    # Metodo per controllare la presenza di nuovi messaggi
    def check_msg(self):
        self.client.check_msg()
    
    # Metodo per ottenere lo stato di connessione
    def get_conn_state(self):
        return self.conn_state