from Subcamada import Subcamada
from Quadro import Quadro
import sys

class Aplicacao(Subcamada):
    def __init__(self):
        Subcamada.__init__(self, sys.stdin, 0)

    def recebe(self, quadro):
        '''Recebe os dados da subcamada inferior, no caso enquadramento, e mostra na tela/terminal'''
        print('Recebeu: {}'.format(quadro.get_dados()))

    def handle(self):
        ''' O handle monitora a porta serial, faz a leitura desse dado, converte
        e enviar para subcamada inferior, no caso enquadramento, realizando o enquadramento
        desse dado '''
        quadro = Quadro()
        dados = sys.stdin.readline().encode('ascii')
        quadro.set_dados(dados)
        self.lower.envia(quadro) #Envia para subcamada inferior
