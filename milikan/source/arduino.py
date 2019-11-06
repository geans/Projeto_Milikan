# Universidade Federal de Alagoas
# Instituto de Física
# Autor: Gean S. Santos
#        Tecnico de Laboratório / Física
# Data: 24 / 08 / 2016
#
# Requirer biblioteca externa
# Instalação:
#   pip install pyserial

from serial import Serial, SerialException
from time import sleep
from sys import platform


def debug(value=''):
    DEBUG = True
    if DEBUG:
        print(value)


class Command:
    init_milikan = b'0'
    change_key = b'1'
    handshake = b'2'
    acknowledge = b'3'


class Arduino:
    port = ''

    def __init__(self):
        if platform[:3] == 'win':
            self.__PORT_RADICAL = 'COM'
        elif platform == 'linux':
            self.__PORT_RADICAL = '/dev/ttyUSB'
        else:
            debug('Erro: sistema operacional não reconhecido.')
            exit()
        self.__port = ''
        self.__backup_port_name = '.port'
        debug('Aguarde. Conectando a Placa Controladora...')
        self.search_port()
        if not self.__port:
            return
        self.__ser = self.return_serial()

    def send_command(self, command):
        if not self.__port:
            debug('Erro: porta do arduino não encontrada')
        else:
            if type(command) == str:
                command = bytes(command.encode('utf-8'))
            try:
                # ser = self.return_serial()
                # sleep(2)
                self.__ser.write(command)
                # sleep(2)
                # ser.close()
            except:
                debug('Erro: variável com tipo inválido. var:', command, ', tipo:', type(command))

    def read_line(self):
        if not self.__port:
            debug('Erro: porta do arduino não encontrada')
        else:
            ser = self.return_serial()
            line = ser.readline()
            ser.close()
            return line

    def search_port(self):
        # verifica última porta usada
        try:
            f = open(self.__backup_port_name, 'r')
            port = f.readline()
            f.close()
            ser = self.return_serial(port)
            sleep(2)  # tempo de guarda
            ser.write(Command.handshake)
            sleep(2)  # tempo de guarda
            ret = ser.read()
            ser.close()
            if ret[:len(Command.acknowledge)] == Command.acknowledge:
                debug('Arduino encontrado na porta: ' + ser.name)
                self.__port = port
                return
        except KeyboardInterrupt:
            debug('\nPrograma interrompido')
            exit()
        except:
            pass

        # procura porta
        self.__port = ''
        max_ports = 15
        debug('Procurando porta com o Arduíno ')
        for port in [self.__PORT_RADICAL + str(i) for i in range(max_ports)]:
            debug(port)
            try:
                # Tenta abrir conexão:
                ser = self.return_serial(port)
                sleep(2)  # tempo de guarda
                ser.write(Command.handshake)
                sleep(2)  # tempo de guarda
                ret = ser.read()
                debug(ret)
                ser.close()
                if ret == Command.acknowledge:
                    debug('\nArduino encontrado na porta: ' + ser.name)
                    self.__port = port
                    f = open(self.__backup_port_name, 'w')
                    f.write(port)  # salva nome da porta em arquivo
                    f.close()
                    return
            except KeyboardInterrupt:
                debug('\nPrograma interrompido')
                exit()
            except (OSError, SerialException):
                pass
        debug()

    def return_serial(self, port=''):
        if port:
            return Serial(port, baudrate=9600, timeout=0.5)
        else:
            return Serial(self.__port, baudrate=9600, timeout=0.5)

    def close_controller(self):
        self.__ser.close()

    @property
    def port_found(self):
        return self.__port

