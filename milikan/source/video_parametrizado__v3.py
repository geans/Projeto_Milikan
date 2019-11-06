import os
import wx
import wx.adv
import cv2
from time import time
from datetime import datetime
from imutils.video import FPS

output = None

def mdebug(value, end='\n'):
    #print('[!]', value, end=end)
    output.write('{}{}'.format(value, end))
    
def mdialog(value, flag='', end='\n'):
    #print(value, end=end)
    output.write('{}{}'.format(value, end))

class Parametro:
    duracao = None
    delta = None
    repeticao = None
    resolucao = None
    agendamento_data = None
    agendamento_hora = None
    diretorio_salvar = None
    
    @staticmethod
    def obter_todos():
        return (Parametro.duracao,
                Parametro.delta,
                Parametro.repeticao,
                Parametro.resolucao,
                Parametro.agendamento_data,
                Parametro.agendamento_hora,
                Parametro.diretorio_salvar)
    
    @staticmethod
    def definir(duracao,
                delta,
                repeticao,
                resolucao,
                agendamento_data,
                agendamento_hora,
                diretorio_salvar):
        Parametro.duracao = duracao.GetValue()
        Parametro.delta = delta.GetValue()
        Parametro.repeticao = repeticao.GetValue()
        Parametro.resolucao = resolucao.GetValue()
        Parametro.agendamento_data = agendamento_data.GetValue()
        Parametro.agendamento_hora = agendamento_hora.GetValue()
        Parametro.diretorio_salvar = diretorio_salvar.GetLabel()

def check_parametros():
    try:
        resolucao = Parametro.resolucao.split('x')
        resolucao = (int(resolucao[0]), int(resolucao[1]))
        Parametro.resolucao = resolucao
    except Exception as e:
        #TODO mensagem: resolucao inválida, formatação: LARGURAxALTURA
        mdialog('Erro: resolucao inválida. {}'.format(e))
        return False
    try:
        d = Parametro.delta
        Parametro.delta = int(d.hour*360 + d.minute*60 + d.second)
    except Exception as e:
        #TODO mensagem: parâmetro delta inválido
        mdialog('Erro: delta inválida. {}'.format(e))
        return False
    return True

def esperar_agendamento():
    mdebug('Esperando agendamento para: ', end='')
    d = Parametro.agendamento_data
    h = Parametro.agendamento_hora
    mdebug('{:02}/{:02}/{:04} {:02}:{:02}:{:02}'.format(
        d.day, d.month, d.year, h.hour, h.minute, h.second))
    if type(Parametro.agendamento_data) == wx.DateTime:
        agenda = Parametro.agendamento_data
        while datetime.now().year < agenda.year:
            pass
        while datetime.now().month < agenda.month:
            pass
        while datetime.now().day < agenda.day:
            pass
    else:
        pass # TODO: Mensagem de aviso
    if type(Parametro.agendamento_hora) == wx.DateTime:
        agenda = Parametro.agendamento_hora
        while datetime.now().hour < agenda.hour:
            pass
        while datetime.now().minute < agenda.minute:
            pass
        while datetime.now().second < agenda.second:
            pass
    else:
        pass # TODO: Mensagem de aviso

def gravar(camera):
    fps = FPS()
    agora = datetime.now()
    nome_arquivo = '{:02}-{:02}-{:04}__{:02}-{:02}-{:02}.avi'.format(
                        agora.day, agora.month, agora.year,
                        agora.hour, agora.minute, agora.second)
    
    mdialog('Gravação iniciada.', end=' ')
    nome_completo = os.path.join(Parametro.diretorio_salvar,
                                 nome_arquivo)
    gravacao = cv2.VideoWriter(nome_completo,
                               cv2.VideoWriter_fourcc(*'XVID'),
                               30.0, Parametro.resolucao)
    tempo_termino = time() + Parametro.duracao
    fps.start()
    while time() <= tempo_termino:
        ret, frame = camera.read()
        if ret == True:
            gravacao.write(frame)
        else:
            #TODO mensagem: 'Erro ao ler quadro do vídeo.'
            break
        fps.update()
    fps.stop()
    gravacao.release()
    mdialog('Gravação terminada.')
    return tempo_termino - Parametro.duracao, fps.fps()

# Estrutura principal do programa
def controlar_gravacao():
    # Verificar Parâmetros
    valido = check_parametros()
    if not valido:
        #TODO: mensagem de erro
        mdebug('Erro: algum parametro inválido')
        return
    
    # Verificar Câmera
    mdialog('Aguarde...')
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        mdialog('Câmera não encontrada!')
        return
    camera.set(3, Parametro.resolucao[0])
    camera.set(4, Parametro.resolucao[1])
    
    # Verificar Agendamento
    esperar_agendamento()
    
    # Gravações
    for contador in range(1, Parametro.repeticao + 1):
        atual, fps = gravar(camera)
        proxima = atual + Parametro.delta
        mdialog('FPS: {:5.2f}'.format(fps))
        mdialog('{} de {} gravações completadas.'.format(
            contador, Parametro.repeticao))
        while time() < proxima and contador != Parametro.repeticao:
            pass
    
    # Encerramento
    mdialog('Gravações terminadas.')
    camera.release()
    cv2.destroyAllWindows()
    mdialog('Câmera liberada.\n')

### Layout da Tela ###
app = wx.App() 
window = wx.Frame(None, title = "Vídeo Parametrizado", size=(500,500)) 
panel = wx.Panel(window)

def criar_hbox(args):
    hbox = wx.BoxSizer(wx.HORIZONTAL)
    for item in args:
        hbox.Add(item, 0, wx.ALL|wx.CENTER, 5)
    return hbox

lbl_descricao = wx.StaticText(panel, label="Duração:", size=(150,15))
duracao = wx.SpinCtrl(panel, initial=20)
lbl_ajuda = wx.StaticText(panel, label="(Segundos)")
hbox_duracao = criar_hbox( (lbl_descricao,duracao,lbl_ajuda) )

lbl_descricao = wx.StaticText(panel, label="Delta:", size=(150,15))
delta = wx.adv.TimePickerCtrl(panel,
    dt=wx.DateTime(day=1,month=1,hour=0, minute=0, second=30))
lbl_ajuda = wx.StaticText(panel, label="(Segundos)")
hbox_delta = criar_hbox( (lbl_descricao,delta,lbl_ajuda) )

lbl_descricao = wx.StaticText(panel, label="Número de Repetições:", size=(150,15))
repeticao = wx.SpinCtrl(panel, initial=1)
hbox_repeticao = criar_hbox( (lbl_descricao,repeticao) )

lbl_descricao = wx.StaticText(panel,
    label="Resolução (largura, altura):", size=(150,15))
opcoes = ['640x480', '800x600', '1280x720', '1920x1080']
resolucao = wx.ComboBox(panel, choices=opcoes, value=opcoes[1])
lbl_ajuda = wx.StaticText(panel, label="(LARGURAxALTURA)")
hbox_resolucao = criar_hbox( (lbl_descricao,resolucao,lbl_ajuda) )

lbl_descricao = wx.StaticText(panel, label="Agendamento:", size=(150,15))
agendamento_data = wx.adv.DatePickerCtrl(panel)
agendamento_hora = wx.adv.TimePickerCtrl(panel)
hbox_agendamento = criar_hbox( (lbl_descricao,agendamento_data, agendamento_hora) )

diretorio_salvar = wx.StaticText(panel, label=os.getcwd())
def escolher_diretorio(event):
    diretorio = wx.DirDialog(panel, "Escolha uma pasta")
    if diretorio.ShowModal() == wx.ID_OK:
        mdebug("Sua escolha {}".format(diretorio.GetPath()))
        diretorio_salvar.SetLabel(diretorio.GetPath())
    diretorio.Destroy()
botao_salvar = wx.Button(panel, -1, "Escolher pasta")
botao_salvar.Bind(wx.EVT_BUTTON, escolher_diretorio)
hbox_salvar = criar_hbox( (botao_salvar, diretorio_salvar) )

def iniciar(event):
    Parametro.definir(duracao,
                delta,
                repeticao,
                resolucao,
                agendamento_data,
                agendamento_hora,
                diretorio_salvar)
    controlar_gravacao()

hbox_iniciar = wx.BoxSizer(wx.HORIZONTAL)
botao_iniciar = wx.Button(panel, -1, "Iniciar")
botao_iniciar.Bind(wx.EVT_BUTTON, iniciar)
hbox_iniciar.Add(botao_iniciar, 0, wx.ALL, 5)

output = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(450,500))
hbox_output = wx.BoxSizer(wx.HORIZONTAL)
hbox_output.Add(output, 0, wx.ALL|wx.CENTER, 5)


configuracoes_vbox = wx.BoxSizer(wx.VERTICAL)
configuracoes_vbox.Add(hbox_duracao, 0, wx.ALL, 5)
configuracoes_vbox.Add(hbox_delta, 0, wx.ALL, 5)
configuracoes_vbox.Add(hbox_repeticao, 0, wx.ALL, 5)
configuracoes_vbox.Add(hbox_resolucao, 0, wx.ALL, 5)
configuracoes_vbox.Add(hbox_agendamento, 0, wx.ALL, 5)
configuracoes_vbox.Add(hbox_salvar, 0, wx.ALL, 5)
total_vbox = wx.BoxSizer(wx.VERTICAL)
total_vbox.Add(configuracoes_vbox, 0, wx.ALL|wx.CENTER, 5)
total_vbox.Add(hbox_iniciar, 0, wx.ALL|wx.CENTER, 5)
total_vbox.Add(hbox_output, 0, wx.ALL|wx.CENTER, 5)

panel.SetSizer(total_vbox)

window.Show(True) 
app.MainLoop()