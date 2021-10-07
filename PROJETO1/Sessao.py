from Subcamada import Subcamada
from Quadro import Quadro
from enum import Enum

class Estados(Enum):
    DISCONECTADO = 0
    ESPERA = 1
    CONECTADO = 2
    HALF1 = 3
    HALF2 = 4

class TipoEvento(Enum):
    DR = 0  #Requisição de desconexão
    DC = 1  #Confirmação de desconexão
    CR = 2  #Requisição de conexão
    CC = 3  #Confirmação de conexão
    DATA = 4
    PAYLOAD = 5
    TIMEOUT = 6
    DISCONNECT = 7

class Evento():
    def __init__(self, tipo):
        self.tipo = tipo

class Sessao(Subcamada):
    def __init__(self, tout):
        Subcamada.__init__(self, None, tout)
        self.estado_atual = Estados.DISC
        self.contadorTimeout = 0

    def handle_timeout(self):
        evento = Evento(TipoEvento.TIMEOUT)
        self.mef_arq(evento)
        self.enable_timeout()

    def mef_iniciador(self, evento):
        if self.estado_atual == Estados.DISCONECTADO:
            if evento.tipo == TipoEvento.CR:
                self.estado_atual = Estados.ESPERA

        elif self.estado_atual == Estados.ESPERA:
            if evento.tipo == TipoEvento.TIMEOUT:
                self.enable_timeout()
                self.contadorTimeout += 1
                if self.contadorTimeout > 10:
                    self.estado_atual = Estados.DISCONECTADO
            elif evento.tipo == TipoEvento.CC:
                self.estado_atual = Estados.CONECTADO
                if evento.tipo == TipoEvento.DATA:
                    #TODO FALTA NOTIFICAR PLAYLOAD
                    pass
                elif evento.tipo == TipoEvento.PAYLOAD:
                    #TODO ENVIAR DATA
                    pass

        elif self.estado_atual == Estados.CONECTADO:
            if evento.tipo == TipoEvento.DISCONNECT:
                self.estado_atual = Estados.HALF1
                # TODO ENVIA DR - REQUISIÇÃO DE DESCONEXÃO
            elif evento.tipo == TipoEvento.DATA:
                self.estado_atual = Estados.CONECTADO
                 # TODO FALTA NOTIFICAR PLAYLOAD
            elif evento.tipo == TipoEvento.PAYLOAD:
                 self.estado_atual = Estados.CONECTADO
                 # TODO ENVIA DATA
            elif evento.tipo == TipoEvento.DR:
                self.estado_atual = Estados.HALF2

        elif self.estado_atual == Estados.HALF1:
            if evento.tipo == TipoEvento.DATA:
                self.estado_atual = Estados.HALF1
                # TODO FALTA NOTIFICAR PLAYLOAD
            elif evento.tipo == TipoEvento.DR:
                self.estado_atual = Estados.DISCONECTADO
                #TODO CONFIRMAÇÃO DE DESCONEXÃO

        elif self.estado_atual == Estados.HALF2:
            if evento.tipo == TipoEvento.DC:
                self.estado_atual = Estados.DISCONECTADO

    def mef_passivo(self, evento=None):
        if self.estado_atual == Estados.DISCONECTADO:
            if evento.tipo == TipoEvento.CR:
                #TODO ENVIA UMA CONFIRMAÇÃO DE CONEXÃO
                self.estado_atual = Estados.CONECTADO

        elif self.estado_atual == Estados.CONECTADO:
            if evento.tipo == TipoEvento.DISCONNECT:
                self.estado_atual = Estados.HALF1
                # TODO ENVIA DR - REQUISIÇÃO DE DESCONEXÃO
            elif evento.tipo == TipoEvento.DATA:
                self.estado_atual = Estados.CONECTADO
                 # TODO FALTA NOTIFICAR PLAYLOAD
            elif evento.tipo == TipoEvento.PAYLOAD:
                 self.estado_atual = Estados.CONECTADO
                 # TODO ENVIA DATA
            elif evento.tipo == TipoEvento.DR:
                self.estado_atual = Estados.HALF2

        elif self.estado_atual == Estados.HALF1:
            if evento.tipo == TipoEvento.DATA:
                self.estado_atual = Estados.HALF1
                # TODO FALTA NOTIFICAR PLAYLOAD
            elif evento.tipo == TipoEvento.DR:
                self.estado_atual = Estados.DISCONECTADO
                #TODO CONFIRMAÇÃO DE DESCONEXÃO

        elif self.estado_atual == Estados.HALF2:
            if evento.tipo == TipoEvento.DC:
                self.estado_atual = Estados.DISCONECTADO


    def desconecta(self):
        pass
    '''Quadro recebido da camada superior'''

    def envia(self, quadro):
        pass

    '''Quadro recebido da camada inferior'''
    def recebe(self, quadro):
        pass