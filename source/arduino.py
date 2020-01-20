# Universidade Federal de Alagoas
# Instituto de Física
# Autor: Gean S. Santos
#        Tecnico de Laboratório / Física
# Data: 01/2020
#
# Requirer biblioteca externa
# Instalação:
#   pip install pyserial

from serial import Serial, SerialException
from time import sleep
from sys import platform
import serial.tools.list_ports

def debug(value=''):
    DEBUG = False
    if DEBUG:
        print(value)


class Arduino:
    def __init__(self, baudrate=9600, timeout=0.5):
        self.__ser = None
        debug('Procurando arduino')
        for port in serial.tools.list_ports.comports():
            debug('porta: {}, {}'.format(port, 'arduino' in str(port).lower()))
            if 'arduino' in port.description.lower():
                try:
                    self.__ser = Serial(port.device)
                    debug('Arduino encontrado, porta: {}'.format(str(port)))
                    break
                except Exception as e:
                    self.__ser = None
                    debug('\t Falha, {}'.format(str(e)))

    def send_command(self, command='0'):
        if self.__ser is None:
            debug('Erro: falha na porta serial')
        else:
            if type(command) == str:
                command = bytes(command.encode('utf-8'))
            try:
                self.__ser.write(command)
            except:
                debug('Erro: variável com tipo inválido. var:', command, ', tipo:', type(command))

    def read_line(self):
        if self.__ser is None:
            debug('Erro: falha na porta serial')
        else:
            line = self.__ser.readline()
            return line.decode('utf-8')
    
    def is_open(self):
        return not self.__ser is None

    def close(self):
        self.__ser.close()

