import struct
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from tkinter import Tk, filedialog, messagebox


def convert_dat_file(input_file_path, output_format='csv'):
    with open(input_file_path, "rb") as f:
        data = f.read()

    floats = list(struct.iter_unpack('<f', data))
    flat_floats = [val[0] for val in floats]

    df = pd.DataFrame(flat_floats, columns=['Value'])

    base_name = os.path.splitext(input_file_path)[0]
    if output_format == 'csv':
        output_file = f"{base_name}_converted.csv"
        df.to_csv(output_file, index=False)
    elif output_format == 'txt':
        output_file = f"{base_name}_converted.txt"
        df.to_csv(output_file, index=False, sep='\t')
    else:
        raise ValueError("Unsupported output format. Choose 'csv' or 'txt'.")

    return output_file


def guess_points_per_second(data, min_duration=60, max_duration=600):
    total_points = len(data)
    candidates = [total_points // d for d in range(min_duration, max_duration + 1) if total_points % d == 0]
    if not candidates:
        raise ValueError("Couldn't find a valid points_per_second automatically.")
    return min(candidates, key=lambda x: abs(x - 1000))


def plot_waterfall(file_path):
    if file_path.endswith('.txt'):
        df = pd.read_csv(file_path, sep='\t')
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format.")

    data = df['Value'].values
    points_per_second = guess_points_per_second(data)
    print(f"Estimated points per second: {points_per_second}")

    total_seconds = len(data) // points_per_second
    data = data[:total_seconds * points_per_second]
    reshaped = data.reshape((total_seconds, points_per_second))

    plt.figure(figsize=(10, 8))
    extent = [0, 1, 0, total_seconds]  # x in MHz, since bandwidth = 1 MHz
    plt.imshow(reshaped, aspect='auto', cmap='viridis', origin='lower', extent=extent)
    plt.colorbar(label='Amplitude')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Time (seconds)')
    plt.title('Waterfall Plot of Observation Data')
    plt.tight_layout()
    plt.show()


def main():
    root = Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(title="Select a .dat file", filetypes=[("DAT files", "*.dat")])
    if not file_path:
        return

    try:
        converted_path = convert_dat_file(file_path, output_format='txt')
        plot_waterfall(converted_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    main()
