import serial
import tkinter as tk
from tkinter import ttk

# Configuración UART
puerto = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(puerto, baudrate, timeout=1)

# Estado de los relés
estado_relays = [0] * 6

# Función para enviar comando
def enviar_comando():
    comando = "CMD=FORCE"
    for i, estado in enumerate(estado_relays):
        comando += f",R{i+1}={estado}"
    ser.write((comando + "\n").encode())

# Función para actualizar estado del relé
def toggle_relay(index, estado):
    estado_relays[index] = estado
    enviar_comando()

# Cambiar a modo automático
def set_automatico():
    ser.write(b"CMD=AUTO\n")

# Leer datos desde ESP32
def leer_datos():
    if ser.in_waiting > 0:
        linea = ser.readline().decode().strip()
        if linea:
            procesar_datos(linea)
    root.after(2000, leer_datos)

# Procesar y mostrar datos
def procesar_datos(data):
    try:
        partes = data.split(';')
        for i in range(4):
            t, h = partes[i].split(',')
            temp_labels[i].config(text=t.replace('=', ': '))
            hum_labels[i].config(text=h.replace('=', ': '))
        
        volt_label.config(text=partes[4].replace('=', ': '))
        adc_label.config(text=partes[5].replace('=', ': '))

        for i in range(6):
            estado = partes[6].split(',')[i].split('=')[1]
            relay_labels[i].config(text=f"Relay {i+1}: {'ON' if estado == '1' else 'OFF'}")
    except:
        pass

# GUI
root = tk.Tk()
root.title("Monitoreo ESP32")

# Crear un frame contenedor para organizar mejor los elementos
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0)

# Etiquetas para temperatura y humedad en dos filas
temp_labels = [ttk.Label(frame, text=f"T{i+1}: -- °C") for i in range(4)]
hum_labels = [ttk.Label(frame, text=f"H{i+1}: -- %") for i in range(4)]

for i in range(2):  # Primera fila
    temp_labels[i].grid(row=0, column=i * 2, padx=10, pady=5)
    hum_labels[i].grid(row=0, column=i * 2 + 1, padx=10, pady=5)

for i in range(2, 4):  # Segunda fila
    temp_labels[i].grid(row=1, column=(i - 2) * 2, padx=10, pady=5)
    hum_labels[i].grid(row=1, column=(i - 2) * 2 + 1, padx=10, pady=5)

# Voltaje y ADC en la siguiente fila
volt_label = ttk.Label(frame, text="V: -- V")
adc_label = ttk.Label(frame, text="ADC: --")
volt_label.grid(row=2, column=0, padx=10, pady=5)
adc_label.grid(row=2, column=1, padx=10, pady=5)

# Etiquetas de relés en una cuadrícula 2x3
relay_labels = [ttk.Label(frame, text=f"Relay {i+1}: OFF") for i in range(6)]
for i in range(6):
    relay_labels[i].grid(row=3 + i // 3, column=i % 3, padx=10, pady=5)

# Botones para controlar los relés (ON y OFF en la misma fila)
for i in range(6):
    ttk.Button(frame, text=f"ON", command=lambda i=i: toggle_relay(i, 1)).grid(row=5 + i // 3, column=i % 3, padx=5, pady=5)
    ttk.Button(frame, text=f"OFF", command=lambda i=i: toggle_relay(i, 0)).grid(row=6 + i // 3, column=i % 3, padx=5, pady=5)

# Botón de modo automático
ttk.Button(frame, text="Modo Automático", command=set_automatico).grid(row=8, column=0, columnspan=3, pady=10)

# Iniciar la lectura de datos
root.after(2000, leer_datos)
root.mainloop()
