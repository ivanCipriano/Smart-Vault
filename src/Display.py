from machine import Pin,I2C
import ssd1306
from gfx import GFX

class Display:
    # Costruttore della classe
    def __init__(self, serial, width, height, scl_pin, sda_pin):
        # Inizializza l'oggetto I2C utilizzando i pin specificati
        i2c = I2C(serial, scl=Pin(scl_pin), sda=Pin(sda_pin))
        
        # Crea un'istanza del display OLED con le dimensioni specificate
        self.display = ssd1306.SSD1306_I2C(width, height, i2c)
        
        # Inizializza l'oggetto GFX per il disegno grafico
        self.gfx = GFX(width, height, self.display.pixel)
    
    # Riempie lo schermo con il colore specificato e lo mostra a schermo
    def fill(self, col):
        self.display.fill(col)
        self.display.show()

    # Riempie lo schermo con il colore di sfondo e visualizza il testo sullo schermo    
    def text_fill(self, string, x, y, col=1, fill=0):
        self.display.fill(fill)
        self.display.show()
        self.display.text(string, x, y, col)
        self.display.show()
    
    
    # Visualizza il testo sullo schermo senza riempire lo sfondo
    def text_no_fill(self, string, x, y, col=1):
        self.display.text(string, x, y, col)
        self.display.show()
    
    # Disegna un rettangolo riempito sullo schermo
    def fill_rect(self, x0, y0, xf, yf, col=0):
        self.gfx.fill_rect(x0, y0, xf, yf, col)

    # Disegna un cerchio non riempito sullo schermo
    def circle_no_fill(self, x0, y0, radius, col=1):
        self.gfx.circle(x0, y0, radius, col)
        self.display.show()

    # Disegna un cerchio riempito sullo schermo
    def circle_fill(self, x0, y0, radius, col=1):
        self.gfx.fill_circle(x0, y0, radius, col)
        self.display.show()