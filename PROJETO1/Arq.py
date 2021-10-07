from Subcamada import Subcamada
from Quadro import Quadro
from enum import Enum
import queue
from collections import deque

class Estados(Enum):
    OCIOSO = 0
    ESPERA = 1

class TipoEvento(Enum):
    '''Os eventos DATA e ACK estão
    associados a camada inferior (enquandramento)'''
    DATA = 0  # quadro completo
    ACK = 1  # confirmação de recebimento de quadro
    '''O evento PAYLOAD está associado a camada superior'''
    PAYLOAD = 2  # É o dado
    TIMEOUT = 3

class Evento():
    def __init__(self, tipo, quadro=None):
        self.tipo = tipo
        self.quadro = quadro

class ARQ(Subcamada):
    def __init__(self, tout):
        Subcamada.__init__(self, None, tout)
        self.rx = 0
        self.tx = 0
        self.estado_atual = Estados.OCIOSO
        self.quadro_recebido = Quadro()
        self.filaDeQuadros = deque()
        self.quadro_ack = Quadro()

    def handle_timeout(self):
        evento = Evento(TipoEvento.TIMEOUT)
        self.mef_arq(evento)
        self.enable_timeout()

    def mef_arq(self, evento):
        if self.estado_atual == Estados.OCIOSO:  # ESTADO OCIOSO
            if evento.tipo == TipoEvento.DATA:
                if evento.quadro.get_sequencia() == self.rx:
                    self.quadro_ack.set_ack()
                    self.quadro_ack.set_sequencia(self.rx)
                    self.lower.envia(self.quadro_ack)  # envia a confirmação, quadro ack
                    self.upper.recebe(evento.quadro)  # Envia o quadro para a camada superior
                    self.rx = not self.rx  # muda o valor de RX
                elif evento.quadro.get_sequencia() != self.rx:
                    self.quadro_ack.set_sequencia(evento.quadro.get_sequencia())
                    self.quadro_ack.set_ack()
                    self.lower.envia(self.quadro_ack)  # envia a confirmação, quadro ack
            elif evento.tipo == TipoEvento.PAYLOAD:
                self.enable_timeout()
                self.quadro_enviado = evento.quadro
                evento.quadro.set_data()
                evento.quadro.set_sequencia(self.tx)
                self.lower.envia(evento.quadro)
                self.estado_atual = Estados.ESPERA

        elif self.estado_atual == Estados.ESPERA:
            if evento.tipo == TipoEvento.TIMEOUT:
                self.reload_timeout()
                self.lower.envia(self.quadro_enviado)
            elif evento.tipo == TipoEvento.PAYLOAD:
                self.filaDeQuadros.append(evento.quadro)
            elif evento.tipo == TipoEvento.DATA:
                if evento.quadro.get_sequencia() == self.rx:
                    self.quadro_ack.set_ack()
                    self.quadro_ack.set_sequencia(self.rx)
                    self.lower.envia(self.quadro_ack)  # envia a confirmação, quadro ack
                    self.upper.recebe(evento.quadro)  # Envia o quadro para a camada superior
                    self.rx = not self.rx  # muda o valor de RX
                elif evento.quadro.get_sequencia() != self.rx:
                    self.quadro_ack.set_sequencia(evento.quadro.get_sequencia())
                    self.quadro_ack.set_ack()
                    self.lower.envia(self.quadro_ack)  # envia a confirmação, quadro ack
            elif evento.tipo == TipoEvento.ACK:
                if evento.quadro.get_sequencia() == self.tx:
                    self.tx = not self.tx
                    if len(self.filaDeQuadros) > 0:
                        quadroFila = self.filaDeQuadros.popleft()
                        quadroFila.set_data()
                        quadroFila.set_sequencia(self.tx)
                        self.lower.envia(quadroFila)
                        self.quadro_enviado = quadroFila
                        self.reload_timeout()
                    else:
                        self.disable_timeout()
                        self.estado_atual = Estados.OCIOSO

    '''Quadro recebido da camada superior'''
    def envia(self, quadro):
        evento = Evento(TipoEvento.PAYLOAD, quadro)
        self.mef_arq(evento)

    '''Quadro recebido da camada inferior'''
    def recebe(self, quadro):
        if quadro.is_ack():
            evento = Evento(TipoEvento.ACK, quadro)
        else:
            evento = Evento(TipoEvento.DATA, quadro)
        self.mef_arq(evento)