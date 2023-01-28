import pyvisa, time, math
from math import log10, floor

rm = pyvisa.ResourceManager()
rm.list_resources()

    #Selectr SCPI instrument
inst = rm.open_resource('USB0::0x2A8D::0x1102::MY58270541::INSTR')  #Define variable? Test Equipment named inst

    #Initialize Variables

#inst.baud_rate = 57600
inst.read_termination = '\n'
inst.write_termination = '\n'
#inst.query('*IDN?')

c_volt = 0
stepcount = 10
start_volt = 0
end_volt = 4.5

def reset():
    inst.write(f'APPLy P6V,0, 0')
    inst.write(f'APPLy P25V,0, 0')
    inst.write(f'APPLy N25V,0, 0')

inst.write(f'APPLy P25V,.1, .1')


    # Steps in forloop calculated from ratio and step size
while c_volt <= end_volt:
    inst.write(f'APPLy P6V,{c_volt}, .1')
    #inst.read()
    c_volt += ((end_volt - start_volt)/(stepcount))
    if c_volt >end_volt:
        break
    c_volt = round(c_volt, 2)
    
    #inst.query('MEAS?')
        #Unclear why I can't read the voltage directly off the machine. Will dig into later
    print(c_volt)
    time.sleep(.5)
    #Reset sources to 0V and 0A
reset()




    #Reference Section for commonly used SCPI commands applicable
"""
Common SCPI Commands
Reset - '*RST'

Example Source 1 3.5V 1.5A

inst.write('APPLy P6V,3.5,1.5')
"""


