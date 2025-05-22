# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('TkAgg')  # Force GUI backend
import serial
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.animation import FuncAnimation
import struct
import csv

# Update port name to match your system
ser = serial.Serial('/dev/tty.usbmodem21301', 250000, timeout=0.01)

buffer_size = 500
data = deque([0]*buffer_size, maxlen=buffer_size)

# Open CSV file
csv_file = open('adc_data.csv', 'wb')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['SampleIndex', 'ADC_Value'])  # Header

sample_index = 0  # Global counter for sample index

fig, ax = plt.subplots()
line, = ax.plot(data)
ax.set_ylim(0, 4095)
ax.set_title("Real-Time ADC Plot (Binary Streaming)")
ax.set_xlabel("Sample")
ax.set_ylabel("ADC Value")
plt.grid(True)

def update(frame):
    global sample_index
    try:
        while ser.in_waiting >= 2:
            raw = ser.read(2)
            val = struct.unpack('<H', raw)[0]
            data.append(val)
            csv_writer.writerow([sample_index, val])
            sample_index += 1
    except Exception as e:
        print("Read error:", e)
    line.set_ydata(data)
    line.set_xdata(range(len(data)))
    return line,

ani = FuncAnimation(fig, update, blit=True, interval=10)

# Ensure the file is closed when the window is closed
import atexit
@atexit.register
def cleanup():
    csv_file.close()
    ser.close()

plt.show()
