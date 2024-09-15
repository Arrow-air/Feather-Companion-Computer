import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import math

# Function to add start and stop braces if missing
def add_braces(json_str):
    json_str = json_str.strip()
    if not json_str.startswith('{'):
        json_str = '{' + json_str
    if not json_str.endswith('}'):
        json_str = json_str + '}'
    return json_str

# Function to clean and prepare each row to be valid JSON, ignoring certain keys
def clean_json_string_with_braces(json_str, ignore_keys):
    json_str = add_braces(json_str)  # Ensure braces are present
    json_str = json_str.replace("'", '"')  # Fix single quotes
    json_str = re.sub(r'([0-9]+)(\s+)"', r'\1, "', json_str)  # Fix missing commas
    json_str = re.sub(r'(\w+":\s*\w+)(\s+)(\w+":)', r'\1,\3', json_str)  # Fix spacing issues

    # Load as dictionary
    json_obj = json.loads(json_str)
    
    # Remove the ignored keys
    for key in ignore_keys:
        if key in json_obj:
            del json_obj[key]
    
    return json_obj

# Load the CSV file
file_path = 'Logs/FeatherFlightLog.csv'
data = pd.read_csv(file_path)

# Keys to ignore
ignore_keys = ['switch_states', 'parachute_state', 'latitude', 'longitude', 'flight_time', 'INPin', 'INState', 'OUTPin', 'OUTState', 'TimeStamp']

# Clean and parse data, ignoring the specified keys for all columns in the DataFrame
data_cleaned = []

# Iterate over each row, converting each column into valid JSON
for _, row in data.iterrows():
    row_cleaned = {}
    for col in data.columns:
        try:
            json_str = clean_json_string_with_braces(str(row[col]), ignore_keys)  # Convert each column entry to JSON string
            row_cleaned.update(json_str)  # Merge parsed JSON objects into a single dictionary
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in column {col}: {e}")
    data_cleaned.append(row_cleaned)

# Convert cleaned data into a DataFrame
parsed_data = pd.DataFrame(data_cleaned)

# Set these Boolean variables to control plot behavior
full_screen_mode = True  # Set to True for full-screen plots
generate_concurrently = True  # Set to True to generate all plots concurrently

# Define the number of plots per figure and subplot size (modifiable variables)
num_plots_per_figure = 16
subplot_width = 3  # Width of each subplot
subplot_height = 2  # Height of each subplot

# Compute the layout based on the number of plots per figure (e.g., for 6, it will be 2 rows, 3 columns)
num_columns_in_row = math.ceil(math.sqrt(num_plots_per_figure))
num_rows_in_fig = math.ceil(num_plots_per_figure / num_columns_in_row)

# Group columns into chunks of `num_plots_per_figure` for each figure
columns_to_plot = [col for col in parsed_data.columns if col not in ignore_keys]
num_figures = math.ceil(len(columns_to_plot) / num_plots_per_figure)  # Total number of figures needed

for figure_idx in range(num_figures):
    # Create a new figure with dynamic rows and columns based on num_plots_per_figure
    fig, axs = plt.subplots(num_rows_in_fig, num_columns_in_row, figsize=(subplot_width * num_columns_in_row, subplot_height * num_rows_in_fig))  # Dynamic layout
    axs = axs.flatten()  # Flatten the 2D array of axes to easily iterate over
    
    # Plot up to `num_plots_per_figure` columns per figure
    start_idx = figure_idx * num_plots_per_figure
    end_idx = min(start_idx + num_plots_per_figure, len(columns_to_plot))
    columns_in_figure = columns_to_plot[start_idx:end_idx]
    
    for i, column in enumerate(columns_in_figure):
        axs[i].plot(parsed_data.index, parsed_data[column], label=column)
        axs[i].set_xlabel('Data Point Counter')
        axs[i].set_ylabel(column)
        axs[i].set_title(f'{column}')
        axs[i].legend()
    
    # Turn off unused subplots if there are fewer columns than subplots in the last figure
    for i in range(len(columns_in_figure), len(axs)):
        axs[i].axis('off')

    # Adjust the spacing between subplots to prevent labels and titles from overlapping
    plt.subplots_adjust(hspace=0.5)  # Increase the vertical space between rows

    # Full screen mode option
    if full_screen_mode:
        fig.canvas.manager.window.showMaximized()

    plt.tight_layout()
    
    # Display all figures concurrently
    plt.show(block=False)

# Use plt.show() at the end to block the script and keep it running until all windows are closed
plt.show()
