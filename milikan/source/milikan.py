# Autor Gean da Silva Santos
# Técnico de Laboratório / Física
# Instituto de Física - Universidade Federal de Alagoas
# Data: 24 de agosto de 2016
#
# Requirer biblioteca externa
# Instalação:
#   pip install pyserial
#   pip install opencv-python
#   pip install matplotlib
#
# Caso necessário atualize o pip:
#   pip install --upgrade pip

from arduino import Arduino, Command
from time import time
from tkinter import *
from tkinter import filedialog, messagebox
from datetime import datetime
from threading import Thread
import cv2
#import matplotlib.pyplot as plt
import wx
import wx.adv

# defines
WIDTH = 900
HIGH = 600


def debug(value=''):
    DEBUG = True
    if DEBUG:
        print(value)


class Camera(Thread):
    def __init__(self):
        Thread.__init__(self)
        try:
            self.__captura = cv2.VideoCapture(0)
            self._stop = False
        except:
            debug('Nenhuma webcam conectada.')
            self._stop = True
        
    def stop(self):
        self._stop = True
     
    def run(self):
        try:
            while not self._stop:
                ret, frame = self.__captura.read()
                cv2.imshow("Video", frame)
                k = cv2.waitKey(30) & 0xff
                if k == 27: # escape button
                    break
        except:
            debug('Nenhuma webcam conectada.')
        self.__captura.release()
        cv2.destroyAllWindows()


class Milikan:

    @staticmethod
    def create_box(args, _type):
        box = wx.BoxSizer(_type)
        for item in args:
            box.Add(item, 0, wx.ALL|wx.CENTER, 5)
        return box
        
    def __init__(self, title='Milikan', video='',
                 file_time = 'milikan__tempos.txt',
                 file_charge_radius='milikan__carga_x_raio.txt',):
        self.c1 = 2.73 * 10**-11 # constante 1, unidade: kg.m(m.s)^-1/2
        self.c2 = 6.37 * 10**-5 # constante 2, unidade: (m.s)^1/2
        self.__file_charge_radius = file_charge_radius
        self.__file_time = file_time
        self.__video = video
        hbox = lambda args: Milikan.create_box(args, wx.HORIZONTAL)
        vbox = lambda args: Milikan.create_box(args, wx.VERTICAL)

        # Iniciando janela com pré visualização

        # variáveis de medidas
        self.__output_file = None
        self.__reference_time = -1 # tempo anterior
        self.__buffer = [] # lista das marcações de tempo
        self.__counter = 1
        self.__t1 = None # tempo de descida/subida
        self.__charge = [] # lista de cargas na gotícula
        self.__radius = [] # lista de radio da gotícula

        # Interface gráfica
        self.app = wx.App()
        window = wx.Frame(None, title = "Vídeo Parametrizado", size=(WIDTH,HIGH)) 
        panel = wx.Panel(window)
        self.__panel = panel
        statictext = lambda text, s=(150,15): wx.StaticText(panel, label=text, size=s)
        
        lbl_descript = statictext("Diferença de potencial no capacitor")
        hbox_1 = hbox( [lbl_descript] )
        
        lbl_descript = statictext("U = ", (35,15))
        self.ddp = wx.SpinCtrl(panel, initial=300, size=(50,25), max=650)
        lbl_unity = statictext('(Volts)')
        hbox_2 = hbox( [lbl_descript, self.ddp, lbl_unity] )
        
        lbl_descript = statictext("Número de divisões (30 div = 0,89 mm)", (300,15))
        hbox_3 = hbox( [lbl_descript] )
        
        lbl_descript = statictext("div = ", (35,15))
        self.div = wx.SpinCtrl(panel, initial=10, size=(50,25))
        lbl_unity = statictext('')
        hbox_4 = hbox( [lbl_descript, self.div, lbl_unity] )
        
        lbl_descript = statictext("Carga média na gotícula")
        hbox_5 = hbox( [lbl_descript] )
        self.avg_charge = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox_6 = hbox( [self.avg_charge] )
        
        lbl_descript = statictext("Raio médio da gotícula")
        hbox_7 = hbox( [lbl_descript] )
        self.avg_radius = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox_8 = hbox( [self.avg_radius] )
        
        # Buttons
        button = lambda text: wx.Button(panel, -1, text, size=(170, 25))
        self.change_key_button = button('Chavear (Espaço)')
        self.change_key_button.Bind(wx.EVT_BUTTON, self.change_key)
        #self.change_key_button.Bind(wx.EVT_KEY_DOWN, self.change_key)
        hbox_9 = hbox( [self.change_key_button] )
        
        self.change_and_measure_key_button = button('Chavear e medir (Enter)')
        self.change_and_measure_key_button.Bind(wx.EVT_BUTTON, self.change_and_measure_key)
        hbox_10 = hbox( [self.change_and_measure_key_button] )
        
        self.erase_button = button('Descartar medidas (Deletar)')
        self.erase_button.Bind(wx.EVT_BUTTON, self.init_measures)
        hbox_11 = hbox( [self.erase_button] )
        
        self.save_measures_button = button('Salvar e fazer nova medida')
        self.save_measures_button.Bind(wx.EVT_BUTTON, self.save_measures)
        hbox_12 = hbox( [self.save_measures_button] )
        
        vbox_1 = vbox( [hbox_1, hbox_2, hbox_3, hbox_4, hbox_5, hbox_6,
                        hbox_7, hbox_8, hbox_9, hbox_10, hbox_11, hbox_12] )

        textCtrl = lambda: wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(160,HIGH-25))
        
        self.time_output = textCtrl()
        vbox_2 = vbox( [statictext("Tempo"), self.time_output] )
                 
        self.charge_output = textCtrl()
        vbox_3 = vbox( [statictext("Carga na gotícula"), self.charge_output] )
                 
        self.radius_output = textCtrl()
        vbox_4 = vbox( [statictext("Radio da gotícula"), self.radius_output] )
        
        total_box = hbox( [vbox_1, vbox_2, vbox_3, vbox_4] )
        
        # Conectando com Arduino
        self.__controller = Arduino()
        if not self.__controller.port_found:
            debug('Falha ao conectar com controlador.')
            #exit()
        panel.SetSizer(total_box)
        window.Show(True) 
        self.app.MainLoop()

    def calc(self, t1, t2):
        u = float(self.ddp.GetValue()) # ddp nas placas
        d = float(self.div.GetValue()) * 0.89 * 10**(-3) / 30.0 # distância percorrida pela gotícula
        #c1 = 2.73 * 10**-11 # constante 1, unidade: kg.m(m.s)^-1/2
        #c2 = 6.37 * 10**-5 # constante 2, unidade: (m.s)^1/2
        v1 = d / t1
        v2 = d / t2
        if v1 < v2:
            v1, v2 = v2, v1

        # Carga na gotícula
        q = self.c1 * (v1 + v2) * (v1 - v2)**(0.5) / u

        # Raio da gotícula
        r = self.c2 * (v1 - v2)**(0.5)

        return q, r
    
    def quit_program(self, event=None):
        self.__master.destroy()
        self.__controller.close_controller()
        exit()

    def change_key(self, event=None):
            self.__controller.send_command(Command.change_key)
    
    def output_values(self, time_output, charge_output, radius_output):
        self.time_output.write('{}\n'.format(time_output))
        self.charge_output.write('{}\n'.format(charge_output))
        self.radius_output.write('{}\n'.format(radius_output))
    
    def replace_avg_values(self):
        self.avg_charge.SetValue('')
        self.avg_radius.SetValue('')
        
        avg_q = sum(self.__charge) / len(self.__charge)
        avg_r = sum(self.__radius) / len(self.__radius)
        
        self.avg_charge.write('{:.4e}'.format(avg_q))
        self.avg_radius.write('{:.4e}'.format(avg_r))

    def change_and_measure_key(self, event=None):
        diff_time, charge, radius = 0, '-', '-'
        if self.__reference_time == -1:
            try:
                self.__controller.send_command(Command.change_key)
            except Exception:
                debug('Atenção! Controlador desconectado.')
            self.__reference_time = time()
            self.__buffer.append(diff_time)
        else:
            try:
                self.__controller.send_command(Command.change_key)
            except Exception:
                debug('Atenção! Controlador desconectado.')
            current_time = time()
            diff_time = current_time - self.__reference_time
            self.__reference_time = current_time
            self.__buffer.append(diff_time)
            if self.__t1 is None:
                self.__t1 = diff_time
            else:
                charge, radius = self.calc(self.__t1, diff_time)
                self.__charge.append(charge)
                self.__radius.append(radius)
                self.__t1 = None
                self.replace_avg_values()
        self.output_values(diff_time, charge, radius)
        return diff_time

    def save_measures(self, event):
        fileDialog = wx.FileDialog(self.__panel, "Escolher nome de arquivo",
                                   style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        # save the current contents in the file
        file = open(fileDialog.GetPath(), 'w')
        if file:
            file.write('Tempo\nSegundos\n\n')
            for measure in self.__buffer:
                file.write(str(measure) + '\n')
            file.write('\n\nCarga\tRaio\n')
            file.write('Coulomb\tMetro\n\n')
            for i in range(len(self.__charge)):
                file.write('{:.6}\t{:.6}\n'.format(self.__charge[i], 
                                                   self.__radius[i]))
            self.init_measures()
        file.close()
        #plt.plot(self.__radius, self.__charge, 'ro')
        #plt.ylabel('Q (C)')
        #plt.xlabel('r (m)')
        #plt.show()

    def init_measures(self, event=None):
        self.__reference_time = -1
        self.__buffer = []

        self.time_output.SetValue('')
        self.charge_output.SetValue('')
        self.radius_output.SetValue('')

        self.__t1 = None
        self.__charge = []
        self.__radius = []
        self.avg_charge.SetValue('')
        self.avg_radius.SetValue('')

    def init_output(self, filename='medidas_milikan', mode='a'):
        self.__output_file = open(filename, mode)

    def report_output(self, value):
        print(value)
        self.__output_file.write(str(value) + '\n')

    def close_output(self):
        self.__output_file.close()

    def run(self):
        self.__video.stop()


def main():
    camera = Camera()
    camera.start()
    Milikan(video=camera).run()
    camera.stop()

if __name__ == '__main__':
    main()
