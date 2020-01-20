# Universidade Federal de Alagoas
# Instituto de Física
# Autor: Gean S. Santos
#        Tecnico de Laboratório / Física
# Data: 01/2020

from time import time
from arduino import Arduino
import webinterface


def debug(value=''):
    DEBUG = True
    if DEBUG:
        print(value)


class Milikan:
    def __init__(self):
        self.c1 = 2.73 * 10**-11 # constante 1, unidade: kg.m(m.s)^-1/2
        self.c2 = 6.37 * 10**-5 # constante 2, unidade: (m.s)^1/2

        # variáveis de medidas
        self.__output_file = None
        self.__reference_time = -1 # tempo anterior
        self.__buffer = [] # lista das marcações de tempo
        self.__counter = 1
        self.__t1 = None # tempo de descida/subida
        self.__charge = [] # lista de cargas na gotícula
        self.__radius = [] # lista de radio da gotícula
        
    def run(self):            
        # Conectando com Arduino
        self.__controller = Arduino()
        if not self.__controller.is_open():
            debug('Falha ao conectar com Arduino! Conecte Arduino ao computador.')
        else:
            debug('Arduino detectado')
            webinterface.inject_functions(self.change_key,
                                          self.change_and_measure_key,
                                          self.blow_drops,
                                          self.init_measures,
                                          self.save_measures)
            debug('Interface carregada')
            ips = webinterface.getServerIPs()
            print("IP disponível:")
            for ip in ips:
                print('\t{}'.format(ip))
            webinterface.runserver()
            self.quit_program()

    def change_key(self):
        debug('Funcao chave')
        self.__controller.send_command()

    def change_and_measure_key(self, ddp, divisions):
        debug('Funcao chave e medir: {}, {}'.format(ddp, divisions))
        diff_time, charge, radius = 0, '-', '-'
        if self.__reference_time == -1:
            try:
                self.__controller.send_command()
            except Exception:
                debug('Atenção! Arduino desconectado')
            self.__reference_time = time()
            self.__buffer.append(diff_time)
        else:
            try:
                self.__controller.send_command()
            except Exception:
                debug('Atenção! Arduino desconectado')
            current_time = time()
            diff_time = current_time - self.__reference_time
            self.__reference_time = current_time
            self.__buffer.append(diff_time)
            if self.__t1 is None:
                self.__t1 = diff_time
            else:
                charge, radius = self.calc(self.__t1, diff_time, ddp, divisions)
                self.__charge.append(charge)
                self.__radius.append(radius)
                self.__t1 = None
        return diff_time
        
    def blow_drops(self):
        debug('Funcao gotas')
        pass  #TODO

    def init_measures(self):
        debug('Funcao apagar medidas')
        self.__reference_time = -1
        self.__buffer = []

        self.__t1 = None
        self.__charge = []
        self.__radius = []

    def save_measures(self):
        debug('Funcao salvar medidas')
        filename = 'medidas-milikan.txt'    
        file = open(filename, 'w')
        if file:
            file.write('Tempo\nSegundos\n\n')
            for measure in self.__buffer:
                file.write(str(measure) + '\n')
            file.write('\n\nCarga\tRaio\n')
            file.write('Coulomb\tMetro\n\n')
            for i in range(len(self.__charge)):
                file.write('{:.6}\t{:.6}\n'.format(self.__charge[i], 
                                                   self.__radius[i]))
        file.close()
        self.init_measures()
        return filename

    def calc(self, t1, t2, ddp, divisions):
        u = float(ddp) # ddp nas placas
        d = float(divisions) * 0.89 * 10**(-3) / 30.0 # distância percorrida pela gotícula
        v1 = d / t1
        v2 = d / t2
        if v1 < v2:
            v1, v2 = v2, v1

        # Carga na gotícula
        q = self.c1 * (v1 + v2) * (v1 - v2)**(0.5) / u

        # Raio da gotícula
        r = self.c2 * (v1 - v2)**(0.5)

        return q, r
    
    def quit_program(self):
        self.__controller.close()


def main():
    Milikan().run()

if __name__ == '__main__':
    main()
