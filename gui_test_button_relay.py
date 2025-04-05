import serial
import tkinter as tk

# Configurar puerto serial (ajusta el puerto a /dev/ttyUSB0 o el que sea correcto)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Funciones para controlar los relés
def relay1_on():
    ser.write(b'R1_ON\n')

def relay1_off():
    ser.write(b'R1_OFF\n')

def relay2_on():
    ser.write(b'R2_ON\n')

def relay2_off():
    ser.write(b'R2_OFF\n')

# Crear la ventana principal
root = tk.Tk()
root.title("Control de Relés")

# Botones para el relay 1
frame1 = tk.Frame(root)
frame1.pack(pady=10)
tk.Label(frame1, text="Relay 1").pack()
tk.Button(frame1, text="Encender", command=relay1_on, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(frame1, text="Apagar", command=relay1_off, width=15).pack(side=tk.LEFT, padx=5)

# Botones para el relay 2
frame2 = tk.Frame(root)
frame2.pack(pady=10)
tk.Label(frame2, text="Relay 2").pack()
tk.Button(frame2, text="Encender", command=relay2_on, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(frame2, text="Apagar", command=relay2_off, width=15).pack(side=tk.LEFT, padx=5)

# Iniciar la GUI
root.mainloop()