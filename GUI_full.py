import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QSpacerItem, QSizePolicy, QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel,
    QMainWindow, QStackedWidget, QTableWidget, QTableWidgetItem, QHBoxLayout 
    )
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QColor, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#########################################
# Utilidad para crear gráficas en widgets
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

        for label, color in lines_info:
            line, = self.ax.plot([], [], label=label, color=color)
            self.lines[label] = line
            self.data[label] = []

        self.ax.legend(loc='upper right')
        super().__init__(fig)

    def update_plot(self, new_values: dict):
        self.time.append(len(self.time))
        for label, val in new_values.items():
            self.data[label].append(val)
            if len(self.data[label]) > 50:
                self.data[label] = self.data[label][-50:]
        if len(self.time) > 50:
            self.time = self.time[-50:]
        for label, line in self.lines.items():
            line.set_data(self.time, self.data[label])
        self.ax.set_xlim(max(0, self.time[0]), self.time[-1] + 1)
        all_vals = [v for sublist in self.data.values() for v in sublist]
        if all_vals:
            self.ax.set_ylim(min(all_vals) - 1, max(all_vals) + 1)
        self.figure.tight_layout()
        self.draw()
        


################################
class TemperatureTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True

        self.plot = MultiLinePlotCanvas("Temperatura", "Grados °C", [
            ("Promedio", 'tab:red'),
            ("Sensor 1", 'tab:blue'),
            ("Sensor 2", 'tab:orange'),
            ("Sensor 3", 'tab:green'),
            ("Sensor 4", 'tab:purple'),
        ])
        self.table = QTableWidget()

        self.toggle_btn = QPushButton("Mostrar como tabla")
        self.toggle_btn.setFixedWidth(200)
        self.toggle_btn.clicked.connect(self.toggle_view)

        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.setFixedWidth(200)
        self.back_btn.clicked.connect(go_back_callback)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.toggle_btn)
        self.btn_layout.addWidget(self.back_btn)
        self.btn_container = QWidget()
        self.btn_container.setLayout(self.btn_layout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.btn_container, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
        self.table.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data)
        self.timer.start(1000)

    def simulate_data(self):
        data = {
            "Promedio": round(random.uniform(22.0, 28.0), 2),
            "Sensor 1": round(random.uniform(21.0, 30.0), 2),
            "Sensor 2": round(random.uniform(21.0, 30.0), 2),
            "Sensor 3": round(random.uniform(21.0, 30.0), 2),
            "Sensor 4": round(random.uniform(21.0, 30.0), 2),
        }
        self.plot.update_plot(data)
        if not self.graph_view:
            self.update_table(data)

    def toggle_view(self):
        self.graph_view = not self.graph_view
        if self.graph_view:
            self.table.hide()
            self.plot.show()
            self.toggle_btn.setText("Mostrar como tabla")
        else:
            self.update_table()
            self.plot.hide()
            self.table.show()
            self.toggle_btn.setText("Mostrar como gráfica")

    def update_table(self, latest_data=None):
        num_rows = len(self.plot.time)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Promedio", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"])
        for i in range(num_rows):
            for j, key in enumerate(["Promedio", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]):
                val = self.plot.data[key][i] if i < len(self.plot.data[key]) else ''
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

################################
class SoilHumidityTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True

        self.plot = MultiLinePlotCanvas("Humedad en Tierra", "Porcentaje de humedad %", [
            ("Promedio", 'tab:green'),
            ("Sensor 1", 'tab:blue'),
            ("Sensor 2", 'tab:orange'),
        ])
        self.table = QTableWidget()

        self.toggle_btn = QPushButton("Mostrar como tabla")
        self.toggle_btn.setFixedWidth(200)
        self.toggle_btn.clicked.connect(self.toggle_view)

        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.setFixedWidth(200)
        self.back_btn.clicked.connect(go_back_callback)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.toggle_btn)
        self.btn_layout.addWidget(self.back_btn)
        self.btn_container = QWidget()
        self.btn_container.setLayout(self.btn_layout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.btn_container, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
        self.table.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data)
        self.timer.start(1000)

    def simulate_data(self):
        val1 = round(random.uniform(30.0, 70.0), 2)
        val2 = round(random.uniform(30.0, 70.0), 2)
        avg = round((val1 + val2) / 2, 2)

        data = {
            "Promedio": avg,
            "Sensor 1": val1,
            "Sensor 2": val2
        }
        self.plot.update_plot(data)
        if not self.graph_view:
            self.update_table()

    def toggle_view(self):
        self.graph_view = not self.graph_view
        if self.graph_view:
            self.table.hide()
            self.plot.show()
            self.toggle_btn.setText("Mostrar como tabla")
        else:
            self.update_table()
            self.plot.hide()
            self.table.show()
            self.toggle_btn.setText("Mostrar como gráfica")

    def update_table(self):
        num_rows = len(self.plot.time)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sensor 1 (%)", "Sensor 2 (%)", "Promedio (%)"])
        for i in range(num_rows):
            for j, key in enumerate(["Sensor 1", "Sensor 2", "Promedio"]):
                val = self.plot.data[key][i] if i < len(self.plot.data[key]) else ''
                self.table.setItem(i, j, QTableWidgetItem(str(val)))


##################################
class LightIrrigationTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()

        self.label_luz = QLabel("LUZ: ")
        self.label_bomba = QLabel("BOMBA DE AGUA: ")
        self.label_peltier1 = QLabel("CELDA PELTIER 1: ")
        self.label_peltier2 = QLabel("CELDA PELTIER 2: ")

        self.labels = [self.label_luz, self.label_bomba, self.label_peltier1, self.label_peltier2]

        for lbl in self.labels:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("background-color: red; color: white; font-size: 16px;")

        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.clicked.connect(go_back_callback)

        layout = QVBoxLayout()
        for lbl in self.labels:
            layout.addWidget(lbl)
        layout.addWidget(self.back_btn)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_states)
        self.timer.start(2000)

    def simulate_states(self):
        estados = [random.choice([True, False]) for _ in range(4)]
        for estado, lbl in zip(estados, self.labels):
            if estado:
                lbl.setText(lbl.text().split(":")[0] + ": ENCENDIDA")
                lbl.setStyleSheet("background-color: green; color: white; font-size: 16px;")
            else:
                lbl.setText(lbl.text().split(":")[0] + ": APAGADA")
                lbl.setStyleSheet("background-color: red; color: white; font-size: 16px;")


##############################
class VoltammetryTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()



        # Tres gráficas: DAC (V), ADC (V), Tiempo (s)
        self.plot_dac = MultiLinePlotCanvas("Voltaje de Salida (DAC)", "Voltios (V)", [("DAC", 'tab:blue')])
        self.plot_adc = MultiLinePlotCanvas("Corriente Leída (ADC)", "Voltios (V)", [("ADC", 'tab:orange')])
        self.plot_time = MultiLinePlotCanvas("Intervalo de Tiempo", "Tiempo (ms)", [("Intervalo", 'tab:green')])


        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.setFixedWidth(200)
        self.back_btn.clicked.connect(go_back_callback)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_dac)
        layout.addWidget(self.plot_adc)
        layout.addWidget(self.plot_time)
        layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_voltammetry_data)
        self.timer.start(1000)

    def simulate_voltammetry_data(self):
        # Simulación para fines de prueba
        dac_val = round(random.uniform(-1.0, 1.0), 3)
        adc_val = round(random.uniform(0.0, 3.3), 3)
        interval = random.randint(90, 110)

        self.plot_dac.update_plot({"DAC": dac_val})
        self.plot_adc.update_plot({"ADC": adc_val})
        self.plot_time.update_plot({"Intervalo": interval})

############################
class MainMenu(QWidget):
    def __init__(self, go_temp, go_hum, go_states, go_voltammetry):
        super().__init__()

        # Fondo con imagen
        self.background = QLabel(self)
        pixmap = QPixmap("C:/Users/Aleja/Desktop/GUI_Alex/ciatej_logo.png") 
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.lower()  

        # Título
        self.title = QLabel("Cámara de crecimiento")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; margin-top: 40px; color: white;")
        self.temp_btn = QPushButton("Ver Temperatura")
        self.hum_btn = QPushButton("Ver Humedad en Tierra")
        self.states_btn = QPushButton("Ver Estados del Sistema")
        self.voltammetry_btn = QPushButton("Ver Voltametría")

        for btn in [self.temp_btn, self.hum_btn, self.states_btn]:
            btn.setFixedWidth(250)  
            btn.setStyleSheet("font-size: 16px; padding: 10px;")
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.temp_btn.clicked.connect(go_temp)
        self.hum_btn.clicked.connect(go_hum)
        self.states_btn.clicked.connect(go_states)
        self.voltammetry_btn.clicked.connect(go_voltammetry)


        self.clock_label = QLabel("Hora actual: --:--:--")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("font-size: 14px; color: white; margin-top: 20px;")

        # Centrar elementos
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(self.temp_btn)
        button_layout.addWidget(self.hum_btn)
        button_layout.addWidget(self.states_btn)
        button_layout.addWidget(self.voltammetry_btn)

        spacer = QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title)
        main_layout.addItem(spacer)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.clock_label)
        self.setLayout(main_layout)

        # Actualizar hora
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def resizeEvent(self, event):
        # Ajustar fondo al tamaño de la ventana
        self.background.resize(self.size())

    def update_time(self):
        now = QTime.currentTime()
        self.clock_label.setText(f"Hora actual: {now.toString('HH:mm:ss')}")

##############################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Monitoreo")
        self.setGeometry(100, 100, 800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenu(
            self.show_temp_tab,
            self.show_hum_tab,
            self.show_states_tab,
            self.show_voltammetry_tab
        )
        self.temp_tab = TemperatureTab(self.show_main_menu)
        self.hum_tab = SoilHumidityTab(self.show_main_menu)
        self.states_tab = LightIrrigationTab(self.show_main_menu)
        self.voltammetry_tab = VoltammetryTab(self.show_main_menu)


        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.temp_tab)
        self.stack.addWidget(self.hum_tab)
        self.stack.addWidget(self.states_tab)
        self.stack.addWidget(self.voltammetry_tab)


    def show_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu)

    def show_temp_tab(self):
        self.stack.setCurrentWidget(self.temp_tab)

    def show_hum_tab(self):
        self.stack.setCurrentWidget(self.hum_tab)

    def show_states_tab(self):
        self.stack.setCurrentWidget(self.states_tab)

    def show_voltammetry_tab(self):
        self.stack.setCurrentWidget(self.voltammetry_tab)


# ******** app entry ******** #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
