import sys
import os
import pandas as pd
import json
import re
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QSpinBox, QDoubleSpinBox, QFormLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Function to clean and prepare each row to be valid JSON, ignoring certain keys
def clean_json_string_with_braces(json_str, ignore_keys):
    json_str = json_str.strip()
    if not json_str.startswith('{'):
        json_str = '{' + json_str
    if not json_str.endswith('}'):
        json_str = json_str + '}'
    json_str = json_str.replace("'", '"')
    json_str = re.sub(r'([0-9]+)(\\s+)"', r'\\1, "', json_str)
    json_str = re.sub(r'(\\w+":\\s*\\w+)(\\s+)(\\w+":)', r'\\1,\\3', json_str)

    json_obj = json.loads(json_str)
    for key in ignore_keys:
        if key in json_obj:
            del json_obj[key]
    
    return json_obj

class PlotWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Variables to keep track of plots and navigation
        self.plot_index = 0
        self.plots = []
        self.parsed_data = None

        # Default settings for number of plots per figure and plot size
        self.num_plots_per_figure = 6
        self.subplot_width = 5.0
        self.subplot_height = 3.0

        # Set up the PyQt layout
        self.initUI()

    def initUI(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)

        # Left-side layout (narrow control panel)
        control_layout = QVBoxLayout()
        control_layout.setSpacing(1)

        # Form layout to hold user inputs
        form_layout = QFormLayout()

        # SpinBox for user to specify number of plots per figure
        self.num_plots_spinbox = QSpinBox(self)
        self.num_plots_spinbox.setMinimum(1)
        self.num_plots_spinbox.setValue(self.num_plots_per_figure)
        form_layout.addRow("Plots per Figure:", self.num_plots_spinbox)

        # DoubleSpinBox for user to specify subplot width
        self.width_spinbox = QDoubleSpinBox(self)
        self.width_spinbox.setRange(1.0, 20.0)
        self.width_spinbox.setValue(self.subplot_width)
        form_layout.addRow("Subplot Width:", self.width_spinbox)

        # DoubleSpinBox for user to specify subplot height
        self.height_spinbox = QDoubleSpinBox(self)
        self.height_spinbox.setRange(1.0, 20.0)
        self.height_spinbox.setValue(self.subplot_height)
        form_layout.addRow("Subplot Height:", self.height_spinbox)

        # Buttons for forward, backward, save, and import
        self.btn_prev = QPushButton('Previous Plot', self)
        self.btn_next = QPushButton('Next Plot', self)
        self.btn_save = QPushButton('Save Plot as PNG', self)
        self.btn_import = QPushButton('Import Log File', self)
        self.btn_apply = QPushButton('Apply Settings', self)

        # Label for navigation
        self.label = QLabel('No plot loaded', self)

        # Connect buttons to their actions
        self.btn_prev.clicked.connect(self.previous_plot)
        self.btn_next.clicked.connect(self.next_plot)
        self.btn_save.clicked.connect(self.save_plot)
        self.btn_import.clicked.connect(self.import_log_file)
        self.btn_apply.clicked.connect(self.apply_settings)

        # Add form layout and buttons to the control layout
        control_layout.addWidget(self.btn_import)
        control_layout.addLayout(form_layout)
        control_layout.addWidget(self.btn_apply)
        control_layout.addWidget(self.btn_prev)
        control_layout.addWidget(self.btn_next)
        control_layout.addWidget(self.btn_save)
        control_layout.addWidget(self.label)

        # Right-side layout (wide figure canvas)
        self.canvas = FigureCanvas(plt.figure())
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        # Add layouts to main horizontal layout
        main_layout.addLayout(control_layout, 1)  # Left control panel (1 part)
        main_layout.addWidget(self.canvas, 3)     # Right canvas (3 parts)

        self.setLayout(main_layout)

        self.setWindowTitle('Log File Plot Viewer')
        self.setMinimumSize(QSize(900, 600))
        self.show()

    def resizeEvent(self, event):
        # Adjust the figure size based on window size
        width = self.canvas.width() / self.logicalDpiX()
        height = self.canvas.height() / self.logicalDpiY()
        self.canvas.figure.set_size_inches(width, height)
        self.canvas.draw()

    def apply_settings(self):
        # Apply user settings for number of plots per figure, subplot width, and height
        self.num_plots_per_figure = self.num_plots_spinbox.value()
        self.subplot_width = self.width_spinbox.value()
        self.subplot_height = self.height_spinbox.value()
        self.update_plot()

    def import_log_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Log File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            self.load_log_file(file_path)

    def load_log_file(self, file_path):
        # Load the log file
        data = pd.read_csv(file_path)

        # Keys to ignore
        ignore_keys = ['switch_states', 'parachute_state', 'latitude', 'longitude', 'flight_time', 'INPin', 'INState', 'OUTPin', 'OUTState', 'TimeStamp']

        # Clean and parse data
        data_cleaned = []
        for _, row in data.iterrows():
            row_cleaned = {}
            for col in data.columns:
                try:
                    json_str = clean_json_string_with_braces(str(row[col]), ignore_keys)
                    row_cleaned.update(json_str)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in column {col}: {e}")
            data_cleaned.append(row_cleaned)

        self.parsed_data = pd.DataFrame(data_cleaned)
        self.plots = [col for col in self.parsed_data.columns if col not in ignore_keys]
        self.plot_index = 0

        self.update_plot()

    def update_plot(self):
        # Clear the canvas and create new subplots on the existing figure
        self.canvas.figure.clear()

        # Get current settings
        num_columns_in_row = math.ceil(math.sqrt(self.num_plots_per_figure))
        num_rows_in_fig = math.ceil(self.num_plots_per_figure / num_columns_in_row)

        # Create new subplots on the figure associated with the canvas
        axs = self.canvas.figure.subplots(num_rows_in_fig, num_columns_in_row)
        axs = axs.flatten()

        start_idx = self.plot_index * self.num_plots_per_figure
        end_idx = min(start_idx + self.num_plots_per_figure, len(self.plots))
        columns_in_figure = self.plots[start_idx:end_idx]

        for i, column in enumerate(columns_in_figure):
            axs[i].plot(self.parsed_data.index, self.parsed_data[column], label=column)
            axs[i].set_xlabel('Data Point Counter')
            axs[i].set_ylabel(column)
            axs[i].set_title(f'{column}')
            axs[i].legend()

        # Turn off unused subplots if fewer than expected
        for i in range(len(columns_in_figure), len(axs)):
            axs[i].axis('off')

        plt.subplots_adjust(hspace=0.5)

        # Redraw the canvas
        self.canvas.draw()

        # Update label
        self.label.setText(f'Plot {self.plot_index + 1} of {math.ceil(len(self.plots) / self.num_plots_per_figure)}')

    def previous_plot(self):
        if self.parsed_data is not None and self.plot_index > 0:
            self.plot_index -= 1
            self.update_plot()

    def next_plot(self):
        if self.parsed_data is not None and self.plot_index < (len(self.plots) - 1) // self.num_plots_per_figure:
            self.plot_index += 1
            self.update_plot()

    def save_plot(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Plot", "", options=options)
        if folder_path and self.parsed_data is not None:
            columns_in_figure = self.plots[self.plot_index * self.num_plots_per_figure: min((self.plot_index + 1) * self.num_plots_per_figure, len(self.plots))]
            for column in columns_in_figure:
                file_name = os.path.join(folder_path, f'{column}.png')
                self.canvas.figure.savefig(file_name)
                print(f'Saved: {file_name}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlotWindow()
    sys.exit(app.exec_())
