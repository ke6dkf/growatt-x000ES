#!/usr/bin/env python3

from datetime import datetime
import argparse
try:
    from pymodbus.exceptions import ModbusIOException
    from pymodbus.client.sync import ModbusSerialClient as ModbusClient
except:
    print("Unable to import pymodbus modules")

"""
 usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_86f6c62629d4eb11adf3a63d44d319e3-if00-port0 is /dev/ttyUSB0 on protopi01
 
"""

def getsigned(regbyte, intlen = 16):
        unsigned = regbyte % 2**intlen
        return (unsigned - 2**intlen if unsigned >= 2**(intlen-1) else unsigned)


def readholdregs(client, unitid = 1, start = 0, numregs = 1):
    print(f"Reading {numregs} holding registers from Unit #{unitid}, starting at register: {start}")
    if not client.is_socket_open():
        client.connect()
    row = client.read_holding_registers(start, numregs, unit= unitid)
    if type(row) is ModbusIOException:
        print("Exception:", row)
    else:
        print(row.registers)


def readinputregs(client, unitid = 1, start = 0, numregs = 1):
    print(f"Reading {numregs} input registers from Unit #{unitid}, starting at register: {start}")
    if not client.is_socket_open():
        client.connect()
    row = client.read_input_registers(start, numregs, unit= unitid)
    if type(row) is ModbusIOException:
        print("Exception:", row)
    else:
        for idx, register in enumerate(row.registers):
            print( idx + start, getsigned(register) )
            
            
def parse_args():
    cmdhelp = [
        "Enable Debugging", #0
        "Serial device name (Default: /dev/ttyUSB0)", #1
        "Serial baud rate (Default: 9600)", #2
        "Unit ID number on modbus (Default: 1)", #3
        "Register type input/holding (Default: input)", #4
        "Starting register address (Default: 0)", #5
        "Number of register to read (Default: 0)", #6
        "Register Range <start_reg>,<end_reg> (required if -s and -n are not used)"
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help=cmdhelp[0], 
        default=False, action='store_true', dest = "debug"
    )
    parser.add_argument("-p", "--port-id",
        help=cmdhelp[1], dest = "serport", 
        default = '/dev/ttyUSB0', 
    )
    parser.add_argument("-b", "--baud-rate",
        help=cmdhelp[2], dest = "serbaud", 
        default = 9600, 
    )
    parser.add_argument("-u", "--unit-id",
        help=cmdhelp[3], dest = "unitid", 
        default = 1, 
    )
    parser.add_argument("-r", "--register-type",
        help=cmdhelp[4], dest = "reg_type", 
        default = "input", 
    )
    parser.add_argument("-s", "--start-address",
        help=cmdhelp[5], metavar='N',
        dest = "initial_register", default = 0, 
    )
    parser.add_argument("-n", "--num-regs",
        help=cmdhelp[6], metavar='N', 
        dest = "read_bytes", default = 1, 
    )
    parser.add_argument('register_range', metavar='N', type=int, nargs='+',
        help=cmdhelp[7]
    )
    results = parser.parse_args()
    if not any(vars(results).values()):
        parser.error('No arguments provided.')
    return results


def main():
    args = parse_args()
    reg_range = 1
    if len(args.register_range) == 2: reg_range = args.register_range[1]
    client = ModbusClient( method='rtu', port = args.serport, baudrate = args.serbaud, stopbits = 1, parity = 'N', bytesize = 8, timeout = 1)
    if args.debug == True: 
        print(f'Reading {reg_range} registers from the {args.reg_type}_register of unit {args.reg_type}, starting at address: {args.register_range[0]}')
    if args.reg_type == "input":
        if args.debug != True:
            readinputregs(client, args.unitid, args.register_range[0], reg_range) #Reading Panel Power
        else:
            print(f"readinputregs({client}, {args.unitid}, {args.initial_register}, {reg_range})")

    elif args.reg_type == "holding":
        if args.debug != True: 
            readholdregs(client, args.unitid, args.register_range[0], reg_range)
        else:
            print(f"readholdregs({client}, {args.unitid}, {args.register_range[0]}, {reg_range})")
    client.close


if __name__ == '__main__':
    import sys, os
    main()
