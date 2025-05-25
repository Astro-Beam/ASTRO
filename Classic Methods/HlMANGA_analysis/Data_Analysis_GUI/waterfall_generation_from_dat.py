import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import struct
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits

def convert_dat_file(input_file_path, output_format='txt'):
    with open(input_file_path, "rb") as f:
        data = f.read()
    floats = list(struct.iter_unpack('<f', data))
    flat_floats = [val[0] for val in floats]
    df = pd.DataFrame(flat_floats, columns=['Value'])
    base_name = os.path.splitext(input_file_path)[0]
    output_format = output_format.lower()
    if output_format == 'csv':
        output_file = f"{base_name}_converted.csv"
        df.to_csv(output_file, index=False)
    elif output_format == 'txt':
        output_file = f"{base_name}_converted.txt"
        df.to_csv(output_file, index=False, sep='\t')
    elif output_format == 'fits':
        output_file = f"{base_name}_converted.fits"
        hdu = fits.PrimaryHDU(df['Value'].values)
        hdu.writeto(output_file, overwrite=True)
    elif output_format in ['hdf', 'hdf5']:
        output_file = f"{base_name}_converted.{output_format}"
        df.to_hdf(output_file, key='data', mode='w')
    else:
        raise ValueError("Unsupported output format.")
    return output_file

def guess_points_per_second(data, min_duration=60, max_duration=600):
    total_points = len(data)
    candidates = [total_points // d for d in range(min_duration, max_duration + 1) if total_points % d == 0]
    if not candidates:
        raise ValueError("Couldn't find a valid points_per_second automatically.")
    return min(candidates, key=lambda x: abs(x - 1000))

def plot_waterfall(file_path):
    print(f"Reading file for plotting: {file_path}")  # Debug print
    if file_path.endswith('.txt'):
        df = pd.read_csv(file_path, sep='\t')
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Only .txt or .csv supported for plotting.")

    if 'Value' not in df.columns:
        raise ValueError("Missing 'Value' column in the file.")

    data = df['Value'].values
    points_per_second = guess_points_per_second(data)
    total_seconds = len(data) // points_per_second
    data = data[:total_seconds * points_per_second]
    reshaped = data.reshape((total_seconds, points_per_second))

    print(f"Plotting {total_seconds} seconds of data at {points_per_second} points/sec")

    plt.figure(figsize=(10, 8))
    plt.imshow(reshaped, aspect='auto', cmap='viridis', origin='lower')
    plt.colorbar(label='Amplitude')
    plt.xlabel('Points')
    plt.ylabel('Time (seconds)')
    plt.title('Waterfall Plot of Observation Data')
    plt.tight_layout()
    plt.show()

def ask_for_waterfall(converted_path):
    if converted_path.endswith('.txt') or converted_path.endswith('.csv'):
        if messagebox.askyesno("Waterfall Plot", "Do you want to generate a waterfall diagram?"):
            try:
                plot_waterfall(converted_path)
            except Exception as e:
                messagebox.showerror("Plot Error", f"Failed to plot waterfall:\n{str(e)}")
    else:
        messagebox.showinfo("Not Supported", "Waterfall plot only supported for .txt and .csv files.")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("DAT files", "*.dat")])
    if file_path:
        file_label.config(text=f"Selected: {file_path}")
        app.selected_file = file_path

def convert_file():
    if not hasattr(app, 'selected_file'):
        messagebox.showerror("No File", "Please select a .dat file.")
        return
    output_format = format_combo.get()
    try:
        converted_path = convert_dat_file(app.selected_file, output_format)
        messagebox.showinfo("Success", f"File converted and saved to:\n{converted_path}")
        ask_for_waterfall(converted_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Set up GUI
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    app = TkinterDnD.Tk()
except ImportError:
    print("tkinterdnd2 not installed. Falling back to normal tkinter (no drag-and-drop).")
    app = tk.Tk()

app.title("DAT File Converter")
app.geometry("400x300")

def drop(event):
    file_path = event.data.strip('{}')
    if file_path.endswith('.dat'):
        file_label.config(text=f"Selected: {file_path}")
        app.selected_file = file_path
    else:
        messagebox.showerror("Invalid File", "Please drop a valid .dat file.")

# Drag & drop UI
drag_label = tk.Label(app, text="Drag & Drop a .dat file below:", fg='gray')
drag_label.pack(pady=10)

drop_area = tk.Label(app, text="Drop File Here", relief="ridge", height=4, bg="white")
drop_area.pack(padx=10, pady=5, fill='x')
try:
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", drop)
except:
    drop_area.config(text="Drag & Drop not supported.\nInstall 'tkinterdnd2'.")

# File selector and options
select_button = tk.Button(app, text="Select .dat File", command=select_file)
select_button.pack()

file_label = tk.Label(app, text="No file selected")
file_label.pack(pady=5)

tk.Label(app, text="Select output format:").pack()
format_combo = ttk.Combobox(app, values=["txt", "csv", "fits", "hdf", "hdf5"])
format_combo.set("txt")
format_combo.pack(pady=5)

convert_button = tk.Button(app, text="Convert", command=convert_file)
convert_button.pack(pady=20)

app.mainloop()