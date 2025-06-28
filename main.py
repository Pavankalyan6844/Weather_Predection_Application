import sys, requests, webbrowser
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QListWidget, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon
from datetime import datetime, timezone, timedelta
import pytz
import os

# Replace this with your actual API key
API_KEY = "82f5cfecc48773cbc620d52279e30291"

class WeatherDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.initWidgets()
        self.initUI()
        self.get_weather()  # Initial call
        self.auto_refresh()

    def initWidgets(self):
        self.city_input = QLineEdit()
        self.get_weather_button = QPushButton("Get Weather")
        self.city_list = QListWidget()

        self.use_location_checkbox = QCheckBox("📍 Use my location")
        self.unit_checkbox = QCheckBox("🌡️ Show in °F")
        self.dark_mode_checkbox = QCheckBox("🌘 Dark Mode")
        self.open_map_button = QPushButton("🗺️ Open Weather Map")

        self.temperature_label = QLabel()
        self.icon_label = QLabel()
        self.description_label = QLabel()
        self.time_label = QLabel()
        self.forecast_label = QLabel()

    def initUI(self):
        self.setWindowTitle("Weather Dashboard")
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "weather-forecast.png")
        self.setWindowIcon(QIcon(icon_path))  # ✅ Set the window icon

        main_layout = QVBoxLayout()

        # Header
        header = QLabel("🌦️ Weather Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Content layout
        content_layout = QHBoxLayout()

        # === Left Panel (Controls) ===
        controls_box = QVBoxLayout()
        city_input_layout = QHBoxLayout()
        self.city_input.setPlaceholderText("Enter city name...")
        city_input_layout.addWidget(self.city_input)
        city_input_layout.addWidget(self.get_weather_button)
        controls_box.addLayout(city_input_layout)

        controls_box.addWidget(QLabel("🌍 Select City:"))
        controls_box.addWidget(self.city_list)
        controls_box.addWidget(self.use_location_checkbox)
        controls_box.addWidget(self.unit_checkbox)
        controls_box.addWidget(self.dark_mode_checkbox)
        controls_box.addWidget(self.open_map_button)

        controls_frame = QGroupBox("Controls")
        controls_frame.setLayout(controls_box)
        controls_frame.setStyleSheet("QGroupBox { font-weight: bold; }")

        # === Right Panel (Weather Info) ===
        weather_info_layout = QVBoxLayout()

        # Current Weather
        temp_layout = QVBoxLayout()
        self.temperature_label.setStyleSheet("font-size: 26px; font-weight: bold;")
        self.icon_label.setStyleSheet("font-size: 20px;")
        self.icon_label.setFixedSize(180, 180)  # or try 64x64, 128x128 depending on layout
        self.icon_label.setScaledContents(True)  # allows image to scale inside QLabel
        self.get_weather_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                color: #0077cc;
                background-color: #f0f8ff;
                border: 1px solid #0077cc;
                border-radius: 6px;
                padding: 3px 6px;
            }
            QPushButton:hover {
                background-color: #d0ecff;
            }
            QPushButton:pressed {
                background-color: #aad4ff;
            }
        """)
        self.open_map_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                color: #1e90ff;
                background-color: transparent;
                border: none;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #104e8b;
                cursor: pointer;
            }
        """)

        self.description_label.setStyleSheet("font-size: 15px;")
        self.time_label.setStyleSheet("font-size: 14px; color: gray;")
        temp_layout.addWidget(self.temperature_label)
        temp_layout.addWidget(self.icon_label)
        temp_layout.addWidget(self.description_label)
        temp_layout.addWidget(self.time_label)

        temp_box = QGroupBox("Current Weather")
        temp_box.setLayout(temp_layout)

        # Forecast Section
        forecast_layout = QVBoxLayout()
        self.forecast_label.setStyleSheet("font-family: Courier; font-size: 14px;")
        forecast_layout.addWidget(self.forecast_label)
        forecast_box = QGroupBox("📅 5-Day Forecast")
        forecast_box.setLayout(forecast_layout)

        weather_info_layout.addWidget(temp_box)
        weather_info_layout.addWidget(forecast_box)

        # Assemble layout
        content_layout.addWidget(controls_frame, 1)
        content_layout.addLayout(weather_info_layout, 2)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.set_light_theme()

        # Connect events
        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_list.itemClicked.connect(self.city_selected)
        self.unit_checkbox.stateChanged.connect(self.get_weather)
        self.use_location_checkbox.stateChanged.connect(self.get_weather)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_theme)
        self.open_map_button.clicked.connect(lambda: webbrowser.open("https://openweathermap.org/weathermap"))

        # Add sample cities
        self.city_list.addItems(["Bangalore", "Mumbai", "Delhi", "Chennai", "Kolkata", "Hyderabad"])

    def toggle_theme(self):
        if self.dark_mode_checkbox.isChecked():
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #f0f0f0;
            }
            QLineEdit, QListWidget, QGroupBox {
                background-color: #3c3c3c;
                color: white;
            }
            QPushButton {
                background-color: #555;
                color: white;
            }
        """)

    def set_light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                color: #000;
            }
            QLineEdit, QListWidget, QGroupBox {
                background-color: #fff;
                color: black;
            }
            QPushButton {
                background-color: #ddd;
                color: black;
            }
        """)

    def get_weather(self):
        city = self.city_input.text()
        if self.use_location_checkbox.isChecked():
            city = self.get_city_from_ip()

        if not city:
            self.temperature_label.setText("❗ Please enter a city or enable location.")
            return

        try:
            units = "imperial" if self.unit_checkbox.isChecked() else "metric"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={units}"
            response = requests.get(url).json()

            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"].capitalize()
            icon = response["weather"][0]["icon"]

            # Handle timezone correctly
            timezone_offset = response["timezone"]
            offset = timezone(timedelta(seconds=timezone_offset))
            dt = datetime.fromtimestamp(response["dt"], tz=offset)

            formatted_time = dt.strftime("%I:%M %p").lstrip('0').lower()
            formatted_date = dt.strftime("%A, %B %d")

            # Update UI
            self.temperature_label.setText(f"{temp:.0f}° {'F' if units == 'imperial' else 'C'}")
            self.description_label.setText(f"🔍 {desc}")
            self.time_label.setText(f"🕒 {formatted_time}  📅 {formatted_date}")

            # Weather Icon
            icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(icon_url).content)
            self.icon_label.setPixmap(pixmap)
            self.get_forecast(city)
            self.icon_label.setScaledContents(True)

        except Exception as e:
            self.temperature_label.setText("❌ Error fetching data.")
            print(f"Error: {e}")

    def load_icon(self, icon_code):
        url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        response = requests.get(url)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.icon_label.setPixmap(pixmap)

    def get_forecast(self, city):
        units = "imperial" if self.unit_checkbox.isChecked() else "metric"
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={units}"
        response = requests.get(url).json()

        if response.get("cod") != "200":
            self.forecast_label.setText("❗ Could not fetch forecast.")
            return

        forecast_text = ""
        for entry in response["list"]:
            if "12:00:00" in entry["dt_txt"]:
                date = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
                date_str = date.strftime("%A")
                temp = entry["main"]["temp"]
                desc = entry["weather"][0]["description"].capitalize()
                forecast_text += f"{date_str}: {temp:.0f}°, {desc}\n"

        self.forecast_label.setText(forecast_text.strip())

    def get_city_from_ip(self):
        try:
            ip_info = requests.get("https://ipinfo.io").json()
            return ip_info.get("city", "")
        except:
            return ""

    def city_selected(self, item):
        self.city_input.setText(item.text())
        self.get_weather()

    def auto_refresh(self):
        timer = QTimer(self)
        timer.timeout.connect(self.get_weather)
        timer.start(300000)  # 5 minutes in milliseconds


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = WeatherDashboard()
    dashboard.resize(900, 500)
    dashboard.show()
    sys.exit(app.exec_())
