# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import csv
import numpy as np

# ---- CONFIG ----
csv_files = ['adc_data_clean.csv', 'adc_data_reverb.csv', 'adc_data_synthesizer.csv', 'adc_data_pitch.csv', 'adc_data.csv']
labels = ['Clean', 'Reverb', 'Synthesizer', 'Pitch Shift', 'Distortion']
sampling_rate = 48000  # Hz
duration_seconds = 3
samples_to_load = sampling_rate * duration_seconds

def load_last_n_samples(csv_filename, n):
    values = []
    with open(csv_filename, 'rb') as f:
        total_lines = sum(1 for _ in f)
    start_line = max(1, total_lines - n)

    with open(csv_filename, 'rb') as f:
        reader = csv.reader(f)
        header = next(reader)
        for i, row in enumerate(reader, start=1):
            if i < start_line:
                continue
            if len(row) < 2:
                continue
            values.append(int(row[1]))
    return values

# ---- LOAD DATA + FFT ----
all_values = []
all_freqs = []
all_magnitudes = []

for filename in csv_files:
    try:
        values = load_last_n_samples(filename, samples_to_load)
        all_values.append(values)

        # FFT
        y = np.array(values)
        N = len(y)
        yf = np.fft.rfft(y)
        xf = np.fft.rfftfreq(N, d=1.0 / sampling_rate)
        magnitude = np.abs(yf)

        all_freqs.append(xf)
        all_magnitudes.append(magnitude)
    except Exception as e:
        print("Error loading", filename, ":", e)
        all_values.append([0]*samples_to_load)
        all_freqs.append([0])
        all_magnitudes.append([0])

# ---- PLOT ----
fig, axs = plt.subplots(5, 2, figsize=(14, 10), sharex='col')

time_axis = np.linspace(0, duration_seconds, samples_to_load)

for i in range(5):
    # Time domain
    axs[i, 0].plot(time_axis, all_values[i], label=labels[i])
    axs[i, 0].set_ylabel("ADC")
    axs[i, 0].set_title(labels[i] + " - Time Domain")
    axs[i, 0].grid(True)

    # Frequency domain
    axs[i, 1].plot(all_freqs[i], all_magnitudes[i], label=labels[i])
    axs[i, 1].set_xlim(0, sampling_rate / 2)
    axs[i, 1].set_ylabel("Magnitude")
    axs[i, 1].set_title(labels[i] + " - Frequency Domain")
    axs[i, 1].grid(True)

axs[-1, 0].set_xlabel("Time (seconds)")
axs[-1, 1].set_xlabel("Frequency (Hz)")
plt.tight_layout()
plt.show()