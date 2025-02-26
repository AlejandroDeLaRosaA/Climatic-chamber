import time
import board
import pwmio
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Configuración inicial
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
ads.gain = 1
channel = AnalogIn(ads, ADS.P0)

# Configuración PWM en un pin digital (e.g., D18 en Raspberry Pi)
pwm = pwmio.PWMOut(board.D18, frequency=5000, duty_cycle=0)

# Configuración de las barridas
sweep_values = [100, 20, 50, 100, 200, 250, 300]
count = len(sweep_values)
intervals = [0] * count


def intervals_calc():
    for pos in range(count):
        intervals[pos] = int(1000000 / (sweep_values[pos] * 128))


def set_pwm(val):
    # Convierte el valor de 0 a 255 a una escala de 0 a 65535 (duty_cycle)
    pwm.duty_cycle = int(val * 65535 / 255)


def voltage_sweep():
    for pos in range(count):
        n = 0
        while n <= 1:
            for val in range(0, 256):
                set_pwm(val)
                time.sleep(intervals[pos] / 1000000.0)
                captured_val = channel.voltage  # Lectura del ADC en voltios
                print(f"PWM Value: {val}, ADC Voltage: {captured_val:.3f} V, Sweep rate: {sweep_values[pos]} mV/s, Interval: {intervals[pos]} us")

            for val in range(255, -1, -1):
                set_pwm(val)
                time.sleep(intervals[pos] / 1000000.0)
                captured_val = channel.voltage
                print(f"PWM Value: {val}, ADC Voltage: {captured_val:.3f} V, Sweep rate: {sweep_values[pos]} mV/s, Interval: {intervals[pos]} us")

            n += 1


def setup():
    intervals_calc()


def loop():
    voltage_sweep()


if __name__ == "__main__":
    setup()
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        pwm.duty_cycle = 0  # Apaga PWM al terminar
        print("PWM detenido")
