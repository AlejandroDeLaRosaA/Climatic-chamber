import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel,
    QMainWindow, QStackedWidget, QTableWidget, QTableWidgetItem, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Utilidad para crear gráficas en widgets
class LivePlotCanvas(FigureCanvas):
    def __init__(self, title, ylabel, color='tab:blue', parent=None, width=5, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.set_title(title)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], color=color)
        self.data = []
        self.time = []
        super().__init__(fig)

    def update_plot(self, new_val):
        self.data.append(new_val)
        self.time.append(len(self.time))
        if len(self.data) > 50:
            self.data = self.data[-50:]
            self.time = self.time[-50:]
        self.line.set_data(self.time, self.data)
        self.ax.set_xlim(max(0, self.time[0]), self.time[-1] + 1)
        self.ax.set_ylim(min(self.data) - 1, max(self.data) + 1)
        self.draw()


class TemperatureTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True

        # Crear la figura y los ejes para múltiples líneas
        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Temperatura Global e Individual")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("°C")
        self.ax.grid(True)

        # Líneas para promedio y 4 sensores
        self.line_avg, = self.ax.plot([], [], label='Promedio', color='tab:red')
        self.line_s1, = self.ax.plot([], [], label='Sensor 1', color='tab:blue')
        self.line_s2, = self.ax.plot([], [], label='Sensor 2', color='tab:green')
        self.line_s3, = self.ax.plot([], [], label='Sensor 3', color='tab:orange')
        self.line_s4, = self.ax.plot([], [], label='Sensor 4', color='tab:purple')

        self.ax.legend(loc='upper right')

        self.canvas = FigureCanvas(self.fig)

        self.data_avg = []
        self.data_s1 = []
        self.data_s2 = []
        self.data_s3 = []
        self.data_s4 = []
        self.time = []

        self.table = QTableWidget()
        self.toggle_btn = QPushButton("Mostrar como tabla")
        self.toggle_btn.clicked.connect(self.toggle_view)

        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.clicked.connect(go_back_callback)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toggle_btn)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.back_btn)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data)
        self.timer.start(1000)

    def simulate_data(self):
        s1 = round(random.uniform(20.0, 30.0), 2)
        s2 = round(random.uniform(20.0, 30.0), 2)
        s3 = round(random.uniform(20.0, 30.0), 2)
        s4 = round(random.uniform(20.0, 30.0), 2)
        avg = round((s1 + s2 + s3 + s4) / 4, 2)

        self.data_s1.append(s1)
        self.data_s2.append(s2)
        self.data_s3.append(s3)
        self.data_s4.append(s4)
        self.data_avg.append(avg)
        self.time.append(len(self.time))

        if len(self.time) > 50:
            self.time = self.time[-50:]
            self.data_avg = self.data_avg[-50:]
            self.data_s1 = self.data_s1[-50:]
            self.data_s2 = self.data_s2[-50:]
            self.data_s3 = self.data_s3[-50:]
            self.data_s4 = self.data_s4[-50:]

        self.line_avg.set_data(self.time, self.data_avg)
        self.line_s1.set_data(self.time, self.data_s1)
        self.line_s2.set_data(self.time, self.data_s2)
        self.line_s3.set_data(self.time, self.data_s3)
        self.line_s4.set_data(self.time, self.data_s4)

        self.ax.set_xlim(max(0, self.time[0]), self.time[-1] + 1)
        all_data = self.data_avg + self.data_s1 + self.data_s2 + self.data_s3 + self.data_s4
        self.ax.set_ylim(min(all_data) - 1, max(all_data) + 1)
        self.canvas.draw()

        if not self.graph_view:
            self.update_table()

    def toggle_view(self):
        self.graph_view = not self.graph_view
        if self.graph_view:
            self.layout.replaceWidget(self.table, self.canvas)
            self.table.hide()
            self.canvas.show()
            self.toggle_btn.setText("Mostrar como tabla")
        else:
            self.update_table()
            self.layout.replaceWidget(self.canvas, self.table)
            self.canvas.hide()
            self.table.show()
            self.toggle_btn.setText("Mostrar como gráfica")

    def update_table(self):
        self.table.setRowCount(len(self.data_avg))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Promedio (°C)", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"])
        for i in range(len(self.data_avg)):
            self.table.setItem(i, 0, QTableWidgetItem(str(self.data_avg[i])))
            self.table.setItem(i, 1, QTableWidgetItem(str(self.data_s1[i])))
            self.table.setItem(i, 2, QTableWidgetItem(str(self.data_s2[i])))
            self.table.setItem(i, 3, QTableWidgetItem(str(self.data_s3[i])))
            self.table.setItem(i, 4, QTableWidgetItem(str(self.data_s4[i])))


class SoilHumidityTab(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.graph_view = True

        self.plot_avg = LivePlotCanvas("Humedad Promedio", "%", color='tab:green')
        self.plot_1 = LivePlotCanvas("Sensor de Humedad 1", "%", color='tab:blue')
        self.plot_2 = LivePlotCanvas("Sensor de Humedad 2", "%", color='tab:orange')
        self.table = QTableWidget()

        self.toggle_btn = QPushButton("Mostrar como tabla")
        self.toggle_btn.clicked.connect(self.toggle_view)

        self.back_btn = QPushButton("Volver al Menú Principal")
        self.back_btn.clicked.connect(go_back_callback)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toggle_btn)
        self.layout.addWidget(self.plot_avg)
        self.layout.addWidget(self.plot_1)
        self.layout.addWidget(self.plot_2)
        self.layout.addWidget(self.back_btn)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data)
        self.timer.start(1000)

    def simulate_data(self):
        val1 = round(random.uniform(30.0, 70.0), 2)
        val2 = round(random.uniform(30.0, 70.0), 2)
        avg = round((val1 + val2) / 2, 2)

        self.plot_1.update_plot(val1)
        self.plot_2.update_plot(val2)
        self.plot_avg.update_plot(avg)
        if not self.graph_view:
            self.update_table()

    def toggle_view(self):
        self.graph_view = not self.graph_view
        if self.graph_view:
            self.layout.replaceWidget(self.table, self.plot_avg)
            self.layout.insertWidget(2, self.plot_1)
            self.layout.insertWidget(3, self.plot_2)
            self.table.hide()
            self.plot_avg.show()
            self.plot_1.show()
            self.plot_2.show()
            self.toggle_btn.setText("Mostrar como tabla")
        else:
            self.update_table()
            self.layout.removeWidget(self.plot_1)
            self.layout.removeWidget(self.plot_2)
            self.plot_1.hide()
            self.plot_2.hide()
            self.layout.replaceWidget(self.plot_avg, self.table)
            self.plot_avg.hide()
            self.table.show()
            self.toggle_btn.setText("Mostrar como gráfica")

    def update_table(self):
        num_rows = len(self.plot_avg.data)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sensor 1 (%)", "Sensor 2 (%)", "Promedio (%)"])
        for i in range(num_rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(self.plot_1.data[i])))
            self.table.setItem(i, 1, QTableWidgetItem(str(self.plot_2.data[i])))
            self.table.setItem(i, 2, QTableWidgetItem(str(self.plot_avg.data[i])))


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


class MainMenu(QWidget):
    def __init__(self, go_temp, go_hum, go_states):
        super().__init__()

        self.title = QLabel("MENÚ PRINCIPAL")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.temp_btn = QPushButton("Ver Temperatura")
        self.hum_btn = QPushButton("Ver Humedad en Tierra")
        self.states_btn = QPushButton("Ver Estados del Sistema")

        self.temp_btn.clicked.connect(go_temp)
        self.hum_btn.clicked.connect(go_hum)
        self.states_btn.clicked.connect(go_states)

        self.clock_label = QLabel("Hora actual: --:--:--")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("font-size: 14px; margin-top: 20px;")

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.temp_btn)
        layout.addWidget(self.hum_btn)
        layout.addWidget(self.states_btn)
        layout.addStretch()
        layout.addWidget(self.clock_label)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        now = QTime.currentTime()
        self.clock_label.setText(f"Hora actual: {now.toString('HH:mm:ss')}")


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
            self.show_states_tab
        )
        self.temp_tab = TemperatureTab(self.show_main_menu)
        self.hum_tab = SoilHumidityTab(self.show_main_menu)
        self.states_tab = LightIrrigationTab(self.show_main_menu)

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.temp_tab)
        self.stack.addWidget(self.hum_tab)
        self.stack.addWidget(self.states_tab)

    def show_main_menu(self):
        self.stack.setCurrentWidget(self.main_menu)

    def show_temp_tab(self):
        self.stack.setCurrentWidget(self.temp_tab)

    def show_hum_tab(self):
        self.stack.setCurrentWidget(self.hum_tab)

    def show_states_tab(self):
        self.stack.setCurrentWidget(self.states_tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

