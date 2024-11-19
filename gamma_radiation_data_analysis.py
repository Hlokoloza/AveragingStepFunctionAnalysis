# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from google.colab import files

# Step 1: Upload the spreadsheets
uploaded_files = files.upload()  # Upload Excel files

# Step 2: Read and process the spreadsheets
dataframes = {}
colors = {}  # Dictionary to store colors for each spreadsheet

for file_name in uploaded_files.keys():
    try:
        # Prompt the user for a description or name for each spreadsheet
        spreadsheet_name = input(f"Please enter a name for the spreadsheet {file_name}: ")
        
        # Prompt the user for a color for the spreadsheet
        color = input(f"Please enter a color for {spreadsheet_name}: ")
        
        # Read the Excel file directly
        df = pd.read_excel(file_name, decimal=".")  # Assuming . for decimal points
        
        # Convert all data to numeric, coercing errors to NaN
        df = df.apply(pd.to_numeric, errors='coerce')
        
        # Trim all columns to 301 values (first 301 rows)
        df = df.iloc[:301, :]
        
        # Add to the dictionary of dataframes with the user-provided name
        dataframes[spreadsheet_name] = df
        colors[spreadsheet_name] = color  # Store the color for this spreadsheet
    except Exception as e:
        print(f"Error reading {file_name}: {e}")

# Step 3: Plot each spreadsheet's averaged data on the same axes
plt.figure(figsize=(12, 8))  # Create a new figure for the combined plot

# Loop through each spreadsheet and plot its data
for spreadsheet_name, df in dataframes.items():
    # Initialize lists for the average current, standard deviation, SEM, CI, and corresponding voltage values
    avg_currents = []
    std_devs = []  # List to store the standard deviation for each voltage step
    sems = []  # List to store the standard error of the mean for each voltage step
    ci_lower = []  # List for lower bounds of confidence interval
    ci_upper = []  # List for upper bounds of confidence interval
    voltages = []
    
    # Loop through all columns (representing data at different voltage steps)
    for column_index in range(df.shape[1]):
        # Compute the average current for this column (voltage step)
        avg_current = df.iloc[:, column_index].mean()
        
        # Compute the standard deviation for this column
        std_dev = df.iloc[:, column_index].std()
        
        # Compute the standard error of the mean (SEM)
        sem = std_dev / np.sqrt(df.shape[0])
        
        # Compute the 95% confidence interval (CI) using the t-distribution
        confidence_level = 0.95
        dof = df.shape[0] - 1  # Degrees of freedom
        t_value = stats.t.ppf((1 + confidence_level) / 2, dof)  # t value for 95% confidence
        margin_of_error = t_value * sem
        ci_lower_bound = avg_current - margin_of_error
        ci_upper_bound = avg_current + margin_of_error
        
        # Append the average current, standard deviation, SEM, and confidence intervals
        avg_currents.append(avg_current)
        std_devs.append(std_dev)
        sems.append(sem)
        ci_lower.append(ci_lower_bound)
        ci_upper.append(ci_upper_bound)
        voltages.append(column_index + 1)  # Voltage values start from 1V
    
    # Plot the average current points as a straight line
    plt.plot(voltages, avg_currents, label=spreadsheet_name, color=colors[spreadsheet_name], marker='o')
    
    # Add the calculated error as text beside the plot
    for voltage, avg_current, std_dev, sem, ci_lower, ci_upper in zip(voltages, avg_currents, std_devs, sems, ci_lower, ci_upper):
        plt.text(voltage, avg_current, f"SD: {std_dev:.2f}\nSEM: {sem:.2f}\nCI: ({ci_lower:.2f}, {ci_upper:.2f})", 
                 ha='center', va='bottom', fontsize=8, color=colors[spreadsheet_name])

# Customize the plot
plt.xlabel('Voltage (V)')
plt.ylabel('Average Current (mA)')
plt.title('Current Measured from a CNS Irradiated by Different Doses of Gamma Radiation')
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')
plt.grid()
plt.tight_layout()  # Adjust layout for better visibility
plt.show()
