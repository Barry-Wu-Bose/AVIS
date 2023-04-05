#
#	Based on https://github.com/tektronix/keithley/blob/main/Drivers/DMM6500_DAQ6510/DMM6500_Python_VISA_Driver_Win10/DMM6500_VISA_Driver.py
#       Corrected and updated by Paul Williams
#	November 23, 2022
#

import pyvisa as visa
import struct
import math
import time
from enum import Enum

# ======================================================================
#      DEFINE THE DMM CLASS INSTANCE HERE
# ======================================================================
class DMM6500:
    def __init__(self):
        self.echoCmd = 1
        self.myInstr = 0
        self.measurement_functions = ["dmm.FUNC_DC_VOLTAGE",
                             "dmm.FUNC_DC_CURRENT",
                             "dmm.FUNC_AC_VOLTAGE",
                             "dmm.FUNC_AC_CURRENT",
                             "dmm.FUNC_RESISTANCE",
                             "dmm.FUNC_4W_RESISTANCE",]

    # ======================================================================
    #      DEFINE INSTRUMENT CONNECTION AND COMMUNICATIONS FUNCTIONS HERE
    # ======================================================================
    def Connect(self, rsrcMgr, rsrcString, timeout, doIdQuery, doReset, doClear):
        self.myInstr = rsrcMgr.open_resource(rsrcString)
        if doIdQuery == 1:
            print(self.QueryCmd("*IDN?"))
        if doReset == 1:
            self.SendCmd("reset()")
        if doClear == 1:
            self.myInstr.clear()
        self.myInstr.timeout = timeout
        return

    def Disconnect(self):
        self.myInstr.close()
        return

    def SendCmd(self, cmd):
        if self.echoCmd == 1:
            print(cmd)
        self.myInstr.write(cmd)
        return

    def QueryCmd(self, cmd):
        if self.echoCmd == 1:
            print(cmd)
        return self.myInstr.query(cmd)

    # ======================================================================
    #      DEFINE BASIC FUNCTIONS HERE
    # ======================================================================
    def Reset(self):
        sndBuffer = "reset()"
        self.SendCmd(sndBuffer)

    def IDQuery(self):
        sndBuffer = "*IDN?"
        return self.QueryCmd(sndBuffer)

    def LoadScriptFile(self, filePathAndName):
        # This function opens the functions.lua file in the same directory as
        # the Python script and trasfers its contents to the DMM's internal
        # memory. All the functions defined in the file are callable by the
        # controlling program.
        func_file = open(filePathAndName, "r")
        contents = func_file.read()
        func_file.close()

        cmd = "if loadfuncs ~= nil then script.delete('loadfuncs') end"
        self.SendCmd(cmd)

        cmd = "loadscript loadfuncs\n{0}\nendscript".format(contents)
        self.SendCmd(cmd)

        print(self.QueryCmd("loadfuncs()"))
        return

    # ======================================================================
    #      DEFINE MEASUREMENT FUNCTIONS HERE
    # ======================================================================
#
#   Need to add functions for Offset Compensation (RES2W, RES4W) and Open Lead Detector (RES4W).
#   Need to add functions for dmm.measure.filter.enable/type/window
#   Need to add functions for Thermocouple Open Lead Detector, reference temperature,
#       reference junction
#   Need to add functions for setting integration unit, reference impedance for dBM
#       reference level for DB
#

    def SetMeasure_Function(self, *args):   #Tested by Paul W on 22 Nov
        if type(args[0]) != str:
            if args[0] == self.MeasFunc.DCI:
                funcStr = "dmm.FUNC_DC_CURRENT"
            elif args[0] == self.MeasFunc.DCV:
                funcStr = "dmm.FUNC_DC_VOLTAGE"
            elif args[0] == self.MeasFunc.ACV:
                funcStr = "dmm.FUNC_AC_VOLTAGE"
            elif args[0] == self.MeasFunc.ACI:
                funcStr = "dmm.FUNC_AC_CURRENT"
            elif args[0] == self.MeasFunc.RES2W:
                funcStr = "dmm.FUNC_RESISTANCE"
            elif args[0] == self.MeasFunc.RES4W:
                funcStr = "dmm.FUNC_4W_RESISTANCE"
            sndBuffer = "dmm.measure.func = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.MeasFunc.DCV:
                funcStr = "dmm.FUNC_DC_VOLTAGE"
            elif args[1] == self.MeasFunc.DCI:
                funcStr = "dmm.FUNC_DC_CURRENT"
            elif args[1] == self.MeasFunc.ACV:
                funcStr = "dmm.FUNC_AC_VOLTAGE"
            elif args[1] == self.MeasFunc.ACI:
                funcStr = "dmm.FUNC_AC_CURRENT"
            elif args[1] == self.MeasFunc.RES2W:
                funcStr = "dmm.FUNC_RESISTANCE"
            elif args[1] == self.MeasFunc.RES4W:
                funcStr = "dmm.FUNC_4W_RESISTANCE"
            sndBuffer = "{}dmm.ATTR_MEAS_FUNCTION, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_Units(self, *args):      #For voltage and temperature measurements only! Tested by Paul W on 23 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.MeasUnits.V:
                funcStr = "dmm.UNIT_VOLT"
            elif args[0] == self.MeasUnits.DB:
                funcStr = "dmm.UNIT_DB"
            elif args[0] == self.MeasUnits.DBM:
                funcStr = "dmm.UNIT_DBM"
            elif args[0] == self.MeasUnits.C:
                funcStr = "dmm.UNIT_CELSIUS"
            elif args[0] == self.MeasUnits.K:
                funcStr = "dmm.UNIT_KELVIN"
            elif args[0] == self.MeasUnits.F:
                funcStr = "dmm.UNIT_FAHRENHEIT"
            sndBuffer = "dmm.measure.unit = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.MeasUnits.V:
                funcStr = "dmm.UNIT_VOLT"
            elif args[1] == self.MeasUnits.DB:
                funcStr = "dmm.UNIT_DB"
            elif args[1] == self.MeasUnits.DBM:
                funcStr = "dmm.UNIT_DBM"
            elif args[1] == self.MeasUnits.C:
                funcStr = "dmm.UNIT_CELSIUS"
            elif args[1] == self.MeasUnits.K:
                funcStr = "dmm.UNIT_KELVIN"
            elif args[1] == self.MeasUnits.F:
                funcStr = "dmm.UNIT_FAHRENHEIT"
            sndBuffer = "{}dmm.ATTR_MEAS_UNIT, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_Bandwidth(self, *args):  #For AC measurements only! Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.DetectBW.F3Hz:
                funcStr = "dmm.DETECTBW_3HZ"
            elif args[0] == self.DetectBW.F30Hz:
                funcStr = "dmm.DETECTBW_30HZ"
            elif args[0] == self.DetectBW.F300Hz:
                funcStr = "dmm.DETECTBW_300HZ"
            sndBuffer = "dmm.measure.detectorbandwidth = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.DetectBW.F3Hz:
                funcStr = "dmm.DETECTBW_3HZ"
            elif args[1] == self.DetectBW.F30Hz:
                funcStr = "dmm.DETECTBW_30HZ"
            elif args[1] == self.DetectBW.F300Hz:
                funcStr = "dmm.DETECTBW_300HZ"
            sndBuffer = "{}dmm.ATTR_MEAS_DETECTBW, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

#   If autoranging is turned off, a range MUST be specified!
#
#   For example the following syntax are correct:
#       DAQ6510.SetMeasure_Range(ChannelString, DAQ6510.AutoRange.OFF, <range>)
#       DAQ6510.SetMeasure_Range(ChannelString, DAQ6510.AutoRange.ON)
#
#   Anthing else is incorrect.
    def SetMeasure_Range(self, *args):
        if (type(args[0]) != str):          #Not tested
            if args[0] == self.AutoRange.OFF:
                funcStr = "dmm.measure.range = {})".format(args[1])
            elif args[0] == self.AutoRange.ON:
                funcStr = "dmm.measure.autorange = dmm.ON"
            sndBuffer = "{}".format(funcStr)
        else:                               #Tested by Paul W on 27 Feb 2023
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.AutoRange.OFF:
                funcStr = " {}dmm.ATTR_MEAS_RANGE, {})".format(setStr, args[2])
            elif args[1] == self.AutoRange.ON:
                funcStr = "{}dmm.ATTR_MEAS_RANGE_AUTO, dmm.ON)".format(setStr)
            sndBuffer = "{}".format(funcStr)
        self.SendCmd(sndBuffer)
        return


    def SetMeasure_NPLC(self, *args):       #For DC measurements only! Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            sndBuffer = "dmm.measure.nplc = {}".format(args[0])
        else:
            sndBuffer = "channel.setdmm(\"{}\", dmm.ATTR_MEAS_NPLC, {})".format(args[0], args[1])
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_AutoDelay(self, *args):  #Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.DmmState.OFF:
                funcStr = "dmm.DELAY_OFF"
            elif args[0] == self.DmmState.ON:
                funcStr = "dmm.DELAY_ON"
            sndBuffer = "dmm.measure.autodelay = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.DmmState.OFF:
                funcStr = "dmm.DELAY_OFF"
            elif args[1] == self.DmmState.ON:
                funcStr = "dmm.DELAY_ON"
            sndBuffer = "{}dmm.ATTR_MEAS_AUTO_DELAY, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_AutoZero(self, *args):   #For DC measurements only! Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.DmmState.OFF:
                funcStr = "dmm.OFF"
            elif args[0] == self.DmmState.ON:
                funcStr = "dmm.ON"
            sndBuffer = "dmm.measure.autozero.enable = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.DmmState.OFF:
                funcStr = "dmm.OFF"
            elif args[1] == self.DmmState.ON:
                funcStr = "dmm.ON"
            sndBuffer = "{}dmm.ATTR_MEAS_AUTO_ZERO, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_InputImpedance(self, *args): #For DCV measurements only! Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.InputZ.Z_AUTO:
                funcStr = "dmm.IMPEDANCE_AUTO"
            elif args[0] == self.InputZ.Z_10M:
                funcStr = "dmm.IMPEDANCE_10M"
            sndBuffer = "dmm.measure.inputimpedance = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.InputZ.Z_AUTO:
                funcStr = "dmm.IMPEDANCE_AUTO"
            elif args[1] == self.InputZ.Z_10M:
                funcStr = "dmm.IMPEDANCE_10M"
            sndBuffer = "{}dmm.ATTR_MEAS_INPUT_IMPEDANCE, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_Count(self, *args):                      #Tested by Paul W on 22 Nov 2022
        if type(args[0]) != str:
            sndBuffer = "dmm.measure.count = {}".format(args[0])
        else:
            sndBuffer = "channel.setdmm(\"{}\", dmm.ATTR_MEAS_COUNT, {})".format(args[0], args[1])
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_Digits(self,*args):                      #Tested by Paul W on 23 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.Digits.D3_5:
                funcStr = "dmm.DIGITS_3_5"
            elif args[0] == self.Digits.D4_5:
                funcStr = "dmm.DIGITS_4_5"
            elif args[0] == self.Digits.D5_5:
                funcStr = "dmm.DIGITS_5_5"
            elif args[0] == self.Digits.D6_5:
                funcStr = "dmm.DIGITS_6_5"
            sndBuffer = "dmm.measure.displaydigits = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.Digits.D3_5:
                funcStr = "dmm.DIGITS_3_5"
            elif args[1] == self.Digits.D4_5:
                funcStr = "dmm.DIGITS_4_5"
            elif args[1] == self.Digits.D5_5:
                funcStr = "dmm.DIGITS_5_5"
            elif args[1] == self.Digits.D6_5:
                funcStr = "dmm.DIGITS_6_5"
            sndBuffer = "{}dmm.ATTR_MEAS_DIGITS, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterCount(self, *args):                #Tested by Paul W on 29 Nov 2022
        if type(args[0]) != str:
            if args[0] in range(1,101):
                funcStr = str(args[0])
            else:
                funcStr = str(1)
                print("Number of requested counts for filtering is either >100 or <1")
            sndBuffer = "dmm.measure.filter.count = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] in range(1,101):
                funcStr = str(args[1])
            else:
                funcStr = str(1)
                print("Number of requested counts for filtering is either >100, <1, or not an integer")
            sndBuffer = "{}dmm.ATTR_MEAS_FILTER_COUNT, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterType(self, *args):                 #Tested by Paul W on 29 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.FilterType.REP:
                funcStr = "dmm.FILTER_REPEAT_AVG"
            elif args[0] == self.FilterType.MOV:
                funcStr = "dmm.FILTER_MOVING_AVG"
            sndBuffer = "dmm.measure.filter.type = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.FilterType.REP:
                funcStr = "dmm.FILTER_REPEAT_AVG"
            elif args[1] == self.FilterType.MOV:
                print("Moving averages cannot be set on a per channel basis!")
                funcStr = "dmm.FILTER_REPEAT_AVG"
            sndBuffer = "{}dmm.ATTR_MEAS_FILTER_TYPE, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterEn(self, *args):                   #Tested by Paul W on 29 Nov 2022
        if type(args[0]) != str:
            if args[0] == self.dmm.ON:
                funcStr = "dmm.ON"
            elif args[0] == self.dmm.OFF:
                funcStr = "dmm.OFF"
            sndBuffer = "dmm.measure.filter.enable = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if args[1] == self.dmm.ON:
                funcStr = "dmm.ON"
            elif args[1] == self.dmm.OFF:
                funcStr = "dmm.OFF"
            sndBuffer = "{}dmm.ATTR_MEAS_FILTER_ENABLE, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetMeasure_FilterWin(self, *args):                   #Tested by Paul W on 29 Nov 2022
        if type(args[0]) != str:
            if (float(args[0]) <= 10) & (float(args[0]) > 0):
                funcStr = str(args[0])
            else:
                funcStr = str(1)
                print("Requested window size is either >10 or <=0")
            sndBuffer = "dmm.measure.filter.window = {}".format(funcStr)
        else:
            setStr = "channel.setdmm(\"{}\", ".format(args[0])
            if (float(args[1]) <= 10) & (float(args[1]) > 0):
                funcStr = str(args[1])
            else:
                funcStr = str(1)
                print("Requested window size is either >10 or <=0")
            sndBuffer = "{}dmm.ATTR_MEAS_FILTER_WINDOW, {})".format(setStr, funcStr)
        self.SendCmd(sndBuffer)
        return

    def SetDisplay(self, *args):
        if args[0] == self.Bright.OFF:
            funcStr = "display.STATE_LCD_OFF"
        elif args[0] == self.Bright.LCD25:
            funcStr = "display.STATE_LCD_25"
        elif args[0] == self.Bright.LCD75:
            funcStr = "display.STATE_LCD_75"
        elif args[0] == self.Bright.LCD100:
            funcStr = "display.STATE_LCD_100"
        else:
            funcStr = "display.STATE_LCD_50"
        sndBuffer = "display.lightstate = {}".format(funcStr)
        self.SendCmd(sndBuffer)

    def Measure(self, count):
        sndBuffer = "print(dmm.measure.read())"
        return self.QueryCmd(sndBuffer)

    def SetFunction_Temperature(self, *args):           #Tested by Paul W on 23 Nov 2022
        # This function can be used to set up to three different measurement
        # function attributes, but they are expected to be in a certain
        # order....
        #   For simple front/rear terminal measurements:
        #       1. Transducer (TC/RTD/Thermistor)
        #       2. Transducer type
        #   For channel scan measurements:
        #       1. Channel string
        #       2. Transducer
        #       3. Transducer type
        if not (args):
            self.SendCmd("dmm.measure.func = dmm.FUNC_TEMPERATURE")
        else:
            if (type(args[0]) != str):
                self.SendCmd("dmm.measure.func = dmm.FUNC_TEMPERATURE")
                if(args):
                    funcStr = "dmm.measure.transducer"
                    if(args[0] == self.Transducer.TC):
                       setStr = "dmm.TRANS_THERMOCOUPLE"
                    elif(args[0] == self.Transducer.RTD4):
                       setStr = "dmm.TRANS_FOURRTD"
                    elif(args[0] == self.Transducer.RTD3):
                       setStr = "dmm.TRANS_THREERTD"
                    elif(args[0] == self.Transducer.THERM):
                       setStr = "dmm.TRANS_THERMISTOR"
                    sndBuffer = "{} = {}".format(funcStr, setStr)
                    self.SendCmd(sndBuffer)
                if(len(args) > 1):
                    if(args[0] == self.Transducer.TC):
                        funcStr  = "dmm.measure.thermocouple"
                        if (args[1] == self.TCType.B):
                            setStr = "dmm.THERMOCOUPLE_B"   #Not supported on DAQ6510 front pannel
                        elif (args[1] == self.TCType.E):
                            setStr = "dmm.THERMOCOUPLE_E"   #Not supported on DAQ6510 front pannel
                        elif(args[1] == self.TCType.J):
                            setStr = "dmm.THERMOCOUPLE_J"   #Not supported on DAQ6510 front pannel
                        elif (args[1] == self.TCType.K):
                            setStr = "dmm.THERMOCOUPLE_K"
                        elif(args[1] == self.TCType.N):
                            setStr = "dmm.THERMOCOUPLE_N"   #Not supported on DAQ6510 front pannel
                        elif(args[1] == self.TCType.R):
                            setStr = "dmm.THERMOCOUPLE_R"   #Not supported on DAQ6510 front pannel
                        elif(args[1] == self.TCType.S):
                            setStr = "dmm.THERMOCOUPLE_S"   #Not supported on DAQ6510 front pannel
                        elif(args[1] == self.TCType.T):
                            setStr = "dmm.THERMOCOUPLE_T"   #Not supported on DAQ6510 front pannel
                        sndBuffer = "{} = {}".format(funcStr, setStr)
                        self.SendCmd(sndBuffer)
                    elif((args[0] == self.Transducer.RTD4) or (args[0] == self.Transducer.RTD3)):
                        if(args[0] == self.Transducer.RTD4):
                            funcStr = "dmm.measure.fourrtd"
                        if(args[0] == self.Transducer.RTD3):
                            funcStr = "dmm.measure.threertd"

                        if(args[1] == self.RTDType.PT100):
                           rtdType = "dmm.RTD_PT100"
                        elif(args[1] == self.RTDType.PT385):
                           rtdType = "dmm.RTD_PT385"
                        elif(args[1] == self.RTDType.PT3916):
                           rtdType = "dmm.RTD_PT3916"
                        elif(args[1] == self.RTDType.D100):
                           rtdType = "dmm.RTD_D100"
                        elif(args[1] == self.RTDType.F100):
                           rtdType = "dmm.RTD_F100"
                        elif(args[1] == self.RTDType.USER):
                           rtdType = "dmm.RTD_USER"

                        sndBuffer = "{} = {}".format(funcStr, rtdType)
                        self.SendCmd(sndBuffer)
                    elif(args[0] == self.Transducer.THERM):
                        funcStr = "dmm.measure.thermistor"
                        if(args[1] == self.ThermType.TH2252):
                           thrmType = "dmm.THERM_2252"
                        elif(args[1] == self.ThermType.TH5K):
                           thrmType = "dmm.THERM_5000"
                        elif(args[1] == self.ThermType.TH10K):
                           thrmType = "dmm.THERM_10000"
                        sndBuffer = "{} = {}".format(funcStr, thrmType)
                        self.SendCmd(sndBuffer)
            else:
                setStr = "channel.setdmm(\"{}\", ".format(args[0])
                self.SendCmd("{}dmm.ATTR_MEAS_FUNCTION, dmm.FUNC_TEMPERATURE)".format(setStr))
                if(len(args) > 1):
                    if(args[1] == self.Transducer.TC):
                       funcStr = "dmm.TRANS_THERMOCOUPLE"
                       xType  = "dmm.ATTR_MEAS_THERMOCOUPLE"
                    elif(args[1] == self.Transducer.RTD4):
                       funcStr = "dmm.TRANS_FOURRTD"
                       xType  = "dmm.ATTR_MEAS_FOUR_RTD"
                    elif(args[1] == self.Transducer.RTD3):
                       funcStr = "dmm.TRANS_THREERTD"
                       xType  = "dmm.ATTR_MEAS_THREE_RTD"
                    elif(args[1] == self.Transducer.THERM):
                       funcStr = "dmm.TRANS_THERMISTOR"
                       xType  = "dmm.ATTR_MEAS_THERMISTOR"
                    sndBuffer = "{}dmm.ATTR_MEAS_TRANSDUCER, {})".format(setStr, funcStr)
                    self.SendCmd(sndBuffer)
                if(len(args) > 2):
                    setStr = "channel.setdmm(\"{}\", ".format(args[0])
                    if(args[1] == self.Transducer.TC):
                        if (args[2] == self.TCType.B):
                            thmType = "dmm.THERMOCOUPLE_B"   #Not supported on 7708
                        elif(args[2] == self.TCType.E):
                            thmType = "dmm.THERMOCOUPLE_E"   #Not supported on 7708
                        elif(args[2] == self.TCType.J):
                            thmType = "dmm.THERMOCOUPLE_J"
                        elif (args[2] == self.TCType.K):
                            thmType = "dmm.THERMOCOUPLE_K"
                        elif(args[2] == self.TCType.N):
                            thmType = "dmm.THERMOCOUPLE_N"   #Not supported on 7708
                        elif(args[2] == self.TCType.R):
                            thmType = "dmm.THERMOCOUPLE_R"   #Not supported on 7708
                        elif(args[2] == self.TCType.S):
                            thmType = "dmm.THERMOCOUPLE_S"   #Not supported on 7708
                        elif(args[2] == self.TCType.T):
                            thmType = "dmm.THERMOCOUPLE_T"   #Not supported on 7708
                        sndBuffer = "{}{}, {})".format(setStr, xType, thmType)
                        self.SendCmd(sndBuffer)
                    elif((args[1] == self.Transducer.RTD4) or (args[1] == self.Transducer.RTD3)):
                        if(args[2] == self.RTDType.PT100):
                           rtdType = "dmm.RTD_PT100"
                        elif(args[2] == self.RTDType.PT385):
                           rtdType = "dmm.RTD_PT385"
                        elif(args[2] == self.RTDType.PT3916):
                           rtdType = "dmm.RTD_PT3916"
                        elif(args[2] == self.RTDType.D100):
                           rtdType = "dmm.RTD_D100"
                        elif(args[2] == self.RTDType.F100):
                           rtdType = "dmm.RTD_F100"
                        elif(args[2] == self.RTDType.USER):
                           rtdType = "dmm.RTD_USER"
                        sndBuffer = "{}{}, {})".format(setStr, xType, rtdType)
                        self.SendCmd(sndBuffer)
                    if(args[1] == self.Transducer.THERM):
                        if(args[2] == self.ThermType.TH2252):
                           thrmType = "dmm.THERM_2252"
                        elif(args[2] == self.ThermType.TH5K):
                           thrmType = "dmm.THERM_5000"
                        elif(args[2] == self.ThermType.TH10K):
                           thrmType = "dmm.THERM_10000"
                        sndBuffer = "{}{}, {})".format(setStr, xType, thrmType)
                        self.SendCmd(sndBuffer)

        return

    class MeasFunc(Enum):
        DCV = 0
        DCI = 1
        ACV = 2
        ACI = 3
        RES2W = 4
        RES4W = 5

    class MeasUnits(Enum):
        V = 0
        DB = 1
        DBM = 2
        C = 3
        K = 4
        F = 5

    class Digits(Enum):
        D3_5 = 0
        D4_5 = 1
        D5_5 = 2
        D6_5 = 3

    class DetectBW(Enum):
        F3Hz = 0
        F30Hz = 1
        F300Hz = 2

    class InputZ(Enum):
        Z_AUTO = 0
        Z_10M = 1

    class dmm(Enum):
        OFF = 0
        ON = 1

    class DmmState(Enum):
        OFF = 0
        ON = 1

    class AutoRange(Enum):
        OFF = 0
        ON = 1

    class AutoDelay(Enum):
        OFF = 0
        ON = 1

    class FilterType(Enum):
        REP = 0
        MOV = 1

    class Bright(Enum):
        OFF = 0
        LCD25 = 1
        LCD50 = 2
        LCD75 = 3
        LCD100 = 4

    class Transducer(Enum):
        TC = 0
        RTD4 = 1
        RTD3 = 2
        THERM = 3

    class TCType(Enum):
        B = 0
        E = 1
        J = 2
        K = 3
        N = 4
        R = 5
        S = 6
        T = 7

    class RTDType(Enum):
        PT100 = 0
        PT385 = 1
        PT3916 = 2
        D100 = 3
        F100 = 4
        USER = 5

    class ThermType(Enum):
        TH2252 = 0
        TH5K = 1
        TH10K = 2

    def SetScan_BasicAttributes(self, *args):
        self.SendCmd("scan.create(\"{}\")".format(args[0]))

        # Set the scan count
        if(len(args) > 1):
            self.SendCmd("scan.scancount = {}".format(args[1]))

        # Set the time between scans in seconds
        if(len(args) > 2):
            self.SendCmd("scan.scaninterval = {}".format(args[2]))
        return

    def Init(self):
        self.SendCmd("waitcomplete()")
        self.SendCmd("trigger.model.initiate()")
        return

    def GetScan_Status(self):
        return self.QueryCmd("print(trigger.model.state())")

    def GetScan_Data(self, dataCount, startIndex, endIndex):                    ## NOT USED 3/21/23
        #charCnt = 24 * dataCount
        accumCnt = int(self.QueryCmd("print(defbuffer1.n)")[0:-1])
        while(accumCnt < endIndex):
            accumCnt = int(self.QueryCmd("print(defbuffer1.n)")[0:-1])
        rcvBuffer = self.QueryCmd("printbuffer({}, {}, defbuffer1)".format(startIndex, endIndex))[0:-1]
        return rcvBuffer

#################################################################################

    def SetMeasure_ChannelDelay(self, *args):                                   ## Added 3/3/23
        if type(args[0]) != str:                                                ## Added 3/3/23
            sndBuffer = "channel.setdelay = {}".format(args[0])                 ## Added 3/3/23
        else:                                                                   ## Added 3/3/23
            sndBuffer = "channel.setdelay(\"{}\", {})".format(args[0], args[1]) ## Added 3/3/23
        self.SendCmd(sndBuffer)                                                 ## Added 3/3/23

    def ScanCapacity(self, *args):                                                      ## Added 3/22/23
        self.SendCmd("defbuffer1.capacity ={}".format(args[0]))                 ## Added 3/22/23
        self.SendCmd("defbuffer1.clear()")                                      ## Added 3/22/23




