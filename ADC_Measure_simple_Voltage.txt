import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Configuración del bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicialización del ADS1115 (ADC)
ads = ADS.ADS1115(i2c)
ads.gain = 1  # Ganancia del ADC (ajusta según tu rango de voltaje)

# Configuración del canal ADC (usaremos el canal 0)
chan = AnalogIn(ads, ADS.P0)

def setup():
    """
    Configuración inicial.
    """
    print("Inicializando...")

def loop():
    """
    Bucle principal para leer el ADC y calcular el voltaje.
    """
    while True:
        adc_value = chan.value  # Lee el valor del ADC (0-32767)
        voltage = chan.voltage  # Lee el voltaje directamente (en voltios)

        # Imprime el valor del ADC y el voltaje
        print(f"ADC Value: {adc_value} | Voltage: {voltage:.3f} V")

        time.sleep(0.1)  # Espera 100 ms entre lecturas

if __name__ == "__main__":
    setup()
    loop()