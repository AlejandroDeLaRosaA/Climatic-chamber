import serial
import tkinter as tk
from threading import Thread

# Configurar el puerto UART de la Raspberry Pi
SERIAL_PORT = "/dev/serial0"  # O usa "/dev/ttyS0" según la configuración
BAUD_RATE = 9600

# Abrir el puerto serie
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Crear ventana con Tkinter
root = tk.Tk()
root.title("Monitor UART ESP32")
root.geometry("400x300")

# Widget de texto para mostrar datos
text_area = tk.Text(root, height=15, width=50)
text_area.pack()

def read_serial():
    """Función para leer datos del ESP32 y mostrarlos en la ventana."""
    while True:
        if ser.in_waiting:
            data = ser.readline().decode().strip()
            text_area.insert(tk.END, data + "\n")
            text_area.see(tk.END)  # Auto scroll

# Ejecutar lectura de UART en un hilo separado
Thread(target=read_serial, daemon=True).start()

root.mainloop()