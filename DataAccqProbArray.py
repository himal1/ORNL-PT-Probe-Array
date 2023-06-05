import pyvisa
import time
import serial
import numpy as np
from datetime import datetime
import os

# ------------MODIFY HERE BEFORE TAKING DATA---------------------
notes = "B0 ON 0.496"

# 1X SENSITIVITY: volt_mG = 100
# 10X SENSITIVITY: volt_mG = 10

volt_mG = 100


# ------------END/ MODIFY HERE BEFORE TAKING DATA----------------



# Initialize serial communication with Arduino
mcon = serial.Serial('COM3', 9600, timeout = 3)
print('ATMega bootloader is loading')
time.sleep(4)
print('Done.')

# Initialize the Agilent DMM connected to Mag-01H
rm = pyvisa.ResourceManager()
dmm = rm.open_resource('USB0::0x0957::0x0A07::MY48003317::0::INSTR')
print(dmm.query('*IDN?'))

# Reset DMM and configure
dmm.write('*RST')                   # Reset the settings
dmm.write('SENS:VOLT:DC:NPLC 10')   # NPLC = 10 (Can change later)
dmm.write('VOLT:DC:IMP:AUTO 1')     # 10G Input Impedance
dmm.write('VOLT:RANG 1')            # Voltage full scale range
dmm.write('VOLT:ZERO:AUTO 0')       # Turn auto zero off
dmm.write('TRIG:SOUR IMM')          # Trigger immediately
dmm.write('TRIG:DEL 0.1')           # First measurement delay
dmm.write('SAMPLE:SOURCE TIM')
dmm.write('SAMPLE:TIM 200E-3')      # Time gap between the readings
dmm.write('SAMPLE:COUNT 10')        # Number of counts
dmm.write('CALC:STAT ON')           # Enable statistics
dmm.write('CALC:FUNC AVER')         # Select averaging operations

bv_xlocations = np.loadtxt('bv_coordinates/xloc.txt') # Load the positions and convert into cm
bv_ylocations = np.loadtxt('bv_coordinates/yloc.txt')
bv_zlocations = np.loadtxt('bv_coordinates/zloc.txt')

now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")



os.mkdir("results/" + str(now))

bv_xresult = open("results/" + str(now) + "/" + "bx" + ".dat", "w+")
bv_yresult = open("results/" + str(now) + "/" + "by" + ".dat", "w+")
bv_zresult = open("results/" + str(now) + "/" + "bz" + ".dat", "w+")

notesFile = open("results/" + str(now) + "/" + "NOTES" + ".txt", "w+")
notesFile.write(notes)
notesFile.close()

time.sleep(1)

for i in range(0,24):
    #print(i)
    if (i>7):     #using beam interference probe for the broken probe
        continue
    mcon.write((str(i).zfill(2)).encode('ascii'))
    time.sleep(1.0)
    dmm.write('CALC:AVER:CLEAR')
    dmm.write('SENS:VOLT:DC:ZERO:AUTO ONCE')
    dmm.write('INIT')
    time.sleep(3.5)
    volt = -float(dmm.query('CALC:AVER:AVER?'))
    if i==16 or i==19:
        volt = -volt
    volt_std = float(dmm.query('CALC:AVER:SDEV?'))
    mG = round(volt * volt_mG, 3)
    mG_std = round(volt_std * volt_mG, 5)
    print('X Probe #', str(i+1), mG, mG_std)

    currentPosition = bv_xlocations[i]
    bv_xresult.write(str(currentPosition[0]) + " " + str(currentPosition[1]) + " " + str(currentPosition[2]) + " " + str(mG) + "\n")
    #print("Results are written")

for i in range(0,24):
    #print(i)
    if (i>7):     #using beam interference probe for the broken probe
        continue
    mcon.write((str(i+16).zfill(2)).encode('ascii'))
    time.sleep(1.0)
    dmm.write('CALC:AVER:CLEAR')
    dmm.write('SENS:VOLT:DC:ZERO:AUTO ONCE')
    dmm.write('INIT')
    time.sleep(3.5)
    volt = -float(dmm.query('CALC:AVER:AVER?'))
    if i==16 or i==19:
        volt = -volt
    volt_std = float(dmm.query('CALC:AVER:SDEV?'))
    mG = round(volt * volt_mG, 3)
    mG_std = round(volt_std * volt_mG, 5)
    print('X Probe #', str(i+1), mG, mG_std)

    currentPosition = bv_xlocations[i]
    bv_xresult.write(str(currentPosition[0]) + " " + str(currentPosition[1]) + " " + str(currentPosition[2]) + " " + str(mG) + "\n")
    #print("Results are written")
    
for i in [0,1,2,3,4,5,6,7]:
    continue
    mcon.write((str(i + 24).zfill(2)).encode('ascii'))
    #print(i)
    time.sleep(1.0)
    dmm.write('CALC:AVER:CLEAR')
    dmm.write('SENS:VOLT:DC:ZERO:AUTO ONCE')
    dmm.write('INIT')
    time.sleep(3.5)
    volt = -float(dmm.query('CALC:AVER:AVER?'))
    volt_std = float(dmm.query('CALC:AVER:SDEV?'))
    mG = round(volt * volt_mG, 3)
    mG_std = round(volt_std * volt_mG, 5)
    #if i==-11:
        #i=5
    print('Y Probe #', str(i+1), mG, mG_std)
    currentPosition = bv_ylocations[i]
    bv_yresult.write(str(currentPosition[0]) + " " + str(currentPosition[1]) + " " + str(currentPosition[2]) + " " + str(mG) + "\n")
    
for i in range(0,5):
    continue
    mcon.write((str(i + 34).zfill(2)).encode('ascii'))
    time.sleep(1.0)
    dmm.write('CALC:AVER:CLEAR')
    dmm.write('SENS:VOLT:DC:ZERO:AUTO ONCE')
    dmm.write('INIT')
    time.sleep(3.5)
    volt = -float(dmm.query('CALC:AVER:AVER?'))
    volt_std = float(dmm.query('CALC:AVER:SDEV?'))
    mG = round(volt * volt_mG, 3)
    mG_std = round(volt_std * volt_mG, 5)
    print('Z Probe #', str(i+1), mG, mG_std)

    currentPosition = bv_zlocations[i]
    bv_zresult.write(str(currentPosition[0]) + " " + str(currentPosition[1]) + " " + str(currentPosition[2]) + " " + str(mG) + "\n")

mcon.write(b'00')

bv_xresult.close()
bv_yresult.close()
bv_zresult.close()
