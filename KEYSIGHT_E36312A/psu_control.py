import pyvisa
rm = pyvisa.ResourceManager()
rm.list_resources()

inst = rm.open_resource('USB0::0x2A8D::0x1102::MY58270541::INSTR')  #Define variable? Test Equipment named inst

#inst.baud_rate = 57600

inst.read_termination = '\n'
inst.write_termination = '\n'
inst.query('*IDN?')

command_list  = open("ON_PSU.txt", "r").read().split('\n')

for command in command_list:
    print(command)

#print(inst.query("*IDN?"))
#print(inst.query("SYSTem:ERRor?"))

"""
Common SCPI Commands
Reset - '*RST'

Example Source 1 3.5V 1.5A

inst.write('APPLy P6V,3.5,1.5')
"""