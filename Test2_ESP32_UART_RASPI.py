import serial
import tkinter as tk
from threading import Thread

#Configura el puerto serial USB 
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException:
    print(f" No se pudo abrir {SERIAL_PORT}. ")
    exit()

#Interfaz con Tkinter
root = tk.Tk()
root.title("Monitor UART ESP32")
root.geometry("400x300")

text_area = tk.Text(root, height=15, width=50)
text_area.pack()

def read_serial():
    """Lee datos del ESP32 por USB y los muestra en la interfaz."""
    while True:
        if ser.in_waiting:
            data = ser.readline().decode().strip()
            text_area.insert(tk.END, data + "\n")
            text_area.see(tk.END)  

#Ejecutar lectura de UART en un hilo separado
Thread(target=read_serial, daemon=True).start()

root.mainloop()
