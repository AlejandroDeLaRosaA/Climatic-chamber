import sys
import json
import math
from PyQt5.QtWidgets import (
    QApplication, 
    QSpacerItem, 
    QSizePolicy, 
    QWidget,
    QVBoxLayout,
    QPushButton, 
    QLabel, 
    QMainWindow, 
    QStackedWidget, 
    QTableWidget,
    QTableWidgetItem, 
    QHBoxLayout
)
from PyQt5.QtCore import (
    Qt, 
    QThread, 
    pyqtSignal, 
    QTimer, 
    QTime
)

from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial

# Utility for plots
class MultiLinePlotCanvas(FigureCanvas):
    def __init__(self, title, ylabel, lines_info, parent=None, width=5, height=3.2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.set_title(title)
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)
        self.lines = {}
        self.data = {}
        self.time = []
        self.max_points = 50
        for label, color in lines_info:
            line, = self.ax.plot([], [], label=label, color=color)
            self.lines[label] = line
            self.data[label] = []
        self.ax.legend(loc='upper right')
        super().__init__(fig)

    def update_plot(self, new_values: dict):
        t = len(self.time)
        self.time.append(t)

        if len(self.time) > self.max_points:
            self.time = self.time[-self.max_points:]

        for label, val in new_values.items():
            self.data[label].append(val)

            if len(self.data[label]) > self.max_points:
                self.data[label] = self.data[label][-self.max_points:]

        for label, line in self.lines.items():
            dat = self.data[label]
            times = self.time[-len(dat):]
            line.set_data(times, dat)

        self.ax.set_xlim(max(0, self.time[0]), self.time[-1] + 1)
        all_vals = [v for values in self.data.values() for v in values if isinstance(v, (int, float))]

        if all_vals:
            mn = min(all_vals)
            mx = max(all_vals)
            if mn == mx:
                mn -= 1; mx += 1
            self.ax.set_ylim(mn, mx)
        self.figure.tight_layout()
        self.draw()

# Temperature
class TemperatureTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True
        self.plot = MultiLinePlotCanvas("Temperatura", "°C", [
            ("Promedio", 'tab:red'), ("Sensor 1", 'tab:blue'),
            ("Sensor 2", 'tab:orange'), ("Sensor 3", 'tab:green'),
            ("Sensor 4", 'tab:purple')
        ])

        self.table = QTableWidget()
        self.toggle_btn = QPushButton("Mostrar como tabla")
        self.toggle_btn.clicked.connect(self.toggle_view)
        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.clicked.connect(go_back_callback)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.back_btn)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.table)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)
        self.table.hide()

    def update_from_serial(self, data):
        try:
            
            temps = []
            for i in range(1, 5):
                raw = data.get(f"temp{i}")
                temps.append(raw if isinstance(raw, (int, float)) else math.nan)
            avg_raw = data.get("tempAvg")
            avg = avg_raw if isinstance(avg_raw, (int, float)) else math.nan

            # Update if at least one is valid
            if not all(math.isnan(t) for t in temps + [avg]):
                new_data = {
                    "Sensor 1": temps[0],
                    "Sensor 2": temps[1],
                    "Sensor 3": temps[2],
                    "Sensor 4": temps[3],
                    "Promedio": avg
                }
                self.plot.update_plot(new_data)

                if not self.graph_view:
                    self.refresh_table()
        except Exception as e:
            print(f"Error TemperatureTab: {e}")


    def toggle_view(self):
        self.graph_view = not self.graph_view

        if self.graph_view:
            self.table.hide(); self.plot.show(); self.toggle_btn.setText("Mostrar como tabla")
        else:
            self.plot.hide(); self.table.show(); self.refresh_table(); self.toggle_btn.setText("Mostrar como gráfica")

    def refresh_table(self):
        keys = ["Promedio","Sensor 1","Sensor 2","Sensor 3","Sensor 4"]
        times = len(self.plot.time)
        self.table.setRowCount(times); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(keys)
        
        for i in range(times):
            for j,key in enumerate(keys):
                val = self.plot.data[key][i] if i < len(self.plot.data[key]) else ''
                self.table.setItem(i,j, QTableWidgetItem(str(val)))

# Soil humidity
class SoilHumidityTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True
        self.plot = MultiLinePlotCanvas("Humedad Tierra","% Humedad",[
            ("Promedio",'tab:green'), ("Sensor 1",'tab:blue'), ("Sensor 2",'tab:orange')])
        
        self.table = QTableWidget()
        self.toggle_btn = QPushButton("Mostrar como tabla"); 
        self.toggle_btn.clicked.connect(self.toggle_view)
        self.back_btn = QPushButton("Volver al Menú Principal"); 
        self.back_btn.clicked.connect(go_back_callback)

        btn_layout = QHBoxLayout(); 
        btn_layout.addWidget(self.toggle_btn); 
        btn_layout.addWidget(self.back_btn)

        self.layout = QVBoxLayout(); 
        self.layout.addWidget(self.plot); 
        self.layout.addWidget(self.table); 
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout); 
        self.table.hide()

    def update_from_serial(self, data):
        try:
            val1 = float(data.get("hum1", math.nan)); 
            val2 = float(data.get("hum2", math.nan)); 
            avg = float(data.get("humAvg", math.nan))
            if any(math.isnan(x) for x in (val1,val2,avg)): return
            new_data={"Sensor 1":val1,"Sensor 2":val2,"Promedio":avg}
            self.plot.update_plot(new_data)

            if not self.graph_view: self.refresh_table()
        except Exception as e:
            print(f"Error SoilHumidity: {e}")

    def toggle_view(self):
        self.graph_view=not self.graph_view

        if self.graph_view: 
            self.table.hide(); 
            self.plot.show(); 
            self.toggle_btn.setText("Mostrar como tabla")
        else: 
            self.plot.hide(); 
            self.table.show(); 
            self.refresh_table(); 
            self.toggle_btn.setText("Mostrar como gráfica")

    def refresh_table(self):
        keys=["Sensor 1","Sensor 2","Promedio"]
        times=len(self.plot.time)
        self.table.setRowCount(times); self.table.setColumnCount(3); self.table.setHorizontalHeaderLabels(keys)
        for i in range(times):
            for j,key in enumerate(keys):
                val=self.plot.data[key][i] if i<len(self.plot.data[key]) else ''
                self.table.setItem(i,j,QTableWidgetItem(str(val)))

# Light & Irrigation
class LightIrrigationTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.labels=[QLabel("LUZ:"),QLabel("BOMBA DE AGUA:"),QLabel("PELTIER1:"),QLabel("PELTIER2:")]
        self.keys=["rgb","pump","peltier1","peltier2"]; 
        self.names=["LUZ","BOMBA","PELTIER1","PELTIER2"]

        for lbl in self.labels: 
            lbl.setAlignment(Qt.AlignCenter); 
            lbl.setStyleSheet("background:red;color:white;font-size:16px;")

        self.back_btn=QPushButton("Volver"); self.back_btn.clicked.connect(go_back_callback)
        layout=QVBoxLayout(); 
        [layout.addWidget(l) for l in self.labels];
        layout.addWidget(self.back_btn); 
        self.setLayout(layout)

    @staticmethod
    def is_on(val): return str(val).lower() in ["1","true"]

    def update_from_serial(self,data):
        try:
            for lbl,key,name in zip(self.labels,self.keys,self.names):
                st=data.get(key,None)
                if self.is_on(st): lbl.setText(f"{name}: ENCENDIDA"); lbl.setStyleSheet("background:green;color:white;font-size:16px;")
                elif st is not None: lbl.setText(f"{name}: APAGADA"); lbl.setStyleSheet("background:red;color:white;font-size:16px;")
                else: lbl.setText(f"{name}: DESCONOCIDO"); lbl.setStyleSheet("background:gray;color:black;font-size:16px;")
        except Exception as e: print(f"Error LightIrrig: {e}")

# Voltammetry
class VoltammetryTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.plot_dac=MultiLinePlotCanvas("DAC","V",[("DAC (V)",'tab:blue')])
        self.plot_adc=MultiLinePlotCanvas("ADC","V",[("ADC (V)",'tab:orange')])
        self.plot_time=MultiLinePlotCanvas("Intervalo","ms",[("Intervalo (ms)",'tab:green')])

        self.table=QTableWidget(); 
        self.table.setColumnCount(3); 
        self.table.setHorizontalHeaderLabels(["DAC","ADC","Intervalo"])

        self.toggle_btn=QPushButton("Mostrar/Tabla"); 
        self.toggle_btn.clicked.connect(self.toggle_view)
        self.back_btn=QPushButton("Volver"); 
        self.back_btn.clicked.connect(go_back_callback)

        btn_layout=QHBoxLayout(); 
        btn_layout.addWidget(self.toggle_btn);
        btn_layout.addWidget(self.back_btn)
        layout=QVBoxLayout(); 
        layout.addWidget(self.plot_dac); 
        layout.addWidget(self.plot_adc); 
        layout.addWidget(self.plot_time); 
        layout.addWidget(self.table); 
        layout.addLayout(btn_layout)
        self.setLayout(layout); self.table.hide()

        self.dac_vals=[]; 
        self.adc_vals=[]; 
        self.intv=[]

    def update_from_serial(self,data):
        try:
            d=float(data.get("dacValue",math.nan)); 
            a=float(data.get("adcValue",math.nan)); 
            i=int(data.get("scanInterval",0))

            if math.isnan(d) or math.isnan(a): return
            self.dac_vals.append(d); 
            self.adc_vals.append(a); 
            self.intv.append(i)
            self.plot_dac.update_plot({"DAC (V)":d}); 
            self.plot_adc.update_plot({"ADC (V)":a}); 
            self.plot_time.update_plot({"Intervalo (ms)":i})

            if self.table.isVisible(): self.add_row()
        except Exception as e: print(f"Error VoltamTab: {e}")

    def toggle_view(self):
        show=self.plot_dac.isVisible()
        for w in (self.plot_dac,self.plot_adc,self.plot_time): w.setVisible(not show)
        self.table.setVisible(show)
        if show: self.refresh_table()

    def add_row(self):
        i=len(self.dac_vals)-1
        self.table.insertRow(i)
        self.table.setItem(i,0,QTableWidgetItem(str(self.dac_vals[i])));
        self.table.setItem(i,1,QTableWidgetItem(str(self.adc_vals[i])));
        self.table.setItem(i,2,QTableWidgetItem(str(self.intv[i])));

    def refresh_table(self):
        self.table.setRowCount(0)
        for i in range(len(self.dac_vals)):
            self.table.insertRow(i)
            self.table.setItem(i,0,QTableWidgetItem(str(self.dac_vals[i])));
            self.table.setItem(i,1,QTableWidgetItem(str(self.adc_vals[i])));
            self.table.setItem(i,2,QTableWidgetItem(str(self.intv[i])));

# Main menu "welcome" window
class MainMenu(QWidget):
    def __init__(self,g1,g2,g3,g4):
        super().__init__()

        self.background=QLabel(self); 
        p=QPixmap("C:/Users/Aleja/Desktop/GUI_Alex/ciatej_logo.png"); 
        self.background.setPixmap(p); 
        self.background.setScaledContents(True); 
        self.background.lower()
        self.title=QLabel("Cámara bioclimática"); 
        self.title.setAlignment(Qt.AlignCenter); 
        self.title.setStyleSheet("font-size:40px;color:white;")

        btns=[("Ver Temp",g1),("Ver Hum",g2),("Ver States",g3),("Ver Volt",g4)]
        layout=QVBoxLayout(); 
        layout.addWidget(self.title)
        for txt,cb in btns:
            b=QPushButton(txt); 
            b.clicked.connect(cb); 
            b.setFixedWidth(200); 
            layout.addWidget(b)

        self.clock=QLabel(); 
        self.clock.setAlignment(Qt.AlignCenter); 
        layout.addWidget(self.clock)
        s=QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding); 
        layout.addItem(s)
        self.setLayout(layout)
        t=QTimer(); 
        t.timeout.connect(self.update_time); 
        t.start(1000)

    def update_time(self): 
        self.clock.setText(QTime.currentTime().toString('HH:mm:ss'))

# Main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cámara Bioclimática CIATEJ-LINBIA")
        self.resize(800,600)
        self.stack=QStackedWidget(); 
        self.setCentralWidget(self.stack)
        self.menu=MainMenu(self.show_temp,self.show_hum,self.show_states,self.show_volt)
        self.temp=TemperatureTab(self.show_menu); 
        self.hum=SoilHumidityTab(self.show_menu)
        self.states=LightIrrigationTab(self.show_menu); 
        self.volt=VoltammetryTab(self.show_menu)

        for w in [self.menu,self.temp,self.hum,self.states,self.volt]: 
            self.stack.addWidget(w)

    def show_menu(self): 
        self.stack.setCurrentWidget(self.menu)

    def show_temp(self): 
        self.stack.setCurrentWidget(self.temp)

    def show_hum(self): 
        self.stack.setCurrentWidget(self.hum)

    def show_states(self): 
        self.stack.setCurrentWidget(self.states)

    def show_volt(self): 
        self.stack.setCurrentWidget(self.volt)

    def update_all_tabs_from_serial(self,data):

        print(f"Received: {data}")
        self.temp.update_from_serial(data)
        self.hum.update_from_serial(data)
        self.states.update_from_serial(data)
        self.volt.update_from_serial(data)

    def closeEvent(self,evt):
        serial_thread.stop(); serial_thread.wait(); evt.accept()

class SerialReaderThread(QThread):
    data_received = pyqtSignal(dict)

    def __init__(self, port='COM5', baud=115200):
        super().__init__()
        self.ser = serial.Serial(port, baud, timeout=1)
        self.running = True

    def run(self):
        while self.running:
            try:
                raw = self.ser.readline()
                
                try:
                    line = raw.decode('utf-8').strip()
                except UnicodeDecodeError:
                    continue

                if not line:
                    continue

              
                if line.startswith('{') and line.endswith('}'):
                    sanitized = line.replace('nan', 'null').replace('NaN', 'null')
                    try:
                        data = json.loads(sanitized)
                        self.data_received.emit(data)
                    except json.JSONDecodeError:
                        print(f"Bad JSON after sanitize: {sanitized}")
                

            except Exception as e:
                print(f"Error leyendo JSON: {e}")

    def stop(self):
        self.running = False
        try:
            self.ser.close()
        except Exception:
            pass

        # 
        # 
        # read serial lines #
        while self.running:
            try:
                raw = self.serial_port.readline()
                # try to decode as UTF-8
                try:
                    line = raw.decode('utf-8').strip()
                except UnicodeDecodeError:
                    continue

                if not line:
                    continue  # Ignore empty lines

                # only process full JSON lines
                if line.startswith('{') and line.endswith('}'):
                    
                    sanitized = line.replace('nan', 'null').replace('NaN', 'null')
                    try:
                        data = json.loads(sanitized)
                        self.data_received.emit(data)
                    except json.JSONDecodeError:
                        print(f"Bad JSON after sanitize: {sanitized}")
               

            except Exception as e:
                print(f"Error leyendo JSON: {e}")
    
    def stop(self):
        self.running=False
        try:
            self.ser.close()
        except Exception:
            pass

if __name__ == '__main__':

    app=QApplication(sys.argv)
    window=MainWindow(); window.show()
    global serial_thread

    serial_thread=SerialReaderThread('COM5',115200)
    serial_thread.data_received.connect(window.update_all_tabs_from_serial)
    serial_thread.start()
    sys.exit(app.exec_())

