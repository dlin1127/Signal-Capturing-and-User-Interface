# Signal-Capturing-and-User-Interface
This github page consists of 3 different code files. 

# adc_read.ino: 
Target: The code file for the arduino (Specially for the DUE program)
functionality: reads the analog signal from the A0 pin, and transmit the data to the python code arduino3-3.py

# Arduino3-3.py:
Target: This is the Python file for real-time ADC reading, and it plots the signal with matplotlib
Functionality: Reads the signal from the DUE and plot it with matplotlib. 
Note: Upload the adc_read.ino file before using this python file

# csv_read.py:L
Target: This is the python file for reading a csv file and plotting the waveform
Functionality: It plots the data on an interactive window and take FFT on the signal as well. 

