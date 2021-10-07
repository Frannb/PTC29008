from warnings import catch_warnings
import mensagem_protocolo_ativo_pb2 as proto_msg
from BaseProto import Protocolo_Mensagens
from app_server import Ordem, Sistema
from enum import Enum
from socket import *
import json

usuarios = dict()
usuarios = {'joao': '123', 'maria': '456', 'luis': '789'}
lista_ordens = []

class Estado(Enum):
    CONECTADO = 1
    DESCONECTADO = 0
    AUTENTICADO =2

class ServidorProtocolo(Protocolo_Mensagens):
    def __init__(self, socket):
        self.socket = socket
        self.usuario_autenticado = ""
        self.estado = Estado.CONECTADO

    def recebe(self):
        dado = self.socket.recv(8192)
        msg_proto = proto_msg.MsgComando()
        msg_proto.ParseFromString(dado)
        return msg_proto

    def envia(self, msg):
        self.socket.send(msg.SerializeToString())

    def verifica_msg_comando(self, sistema):
        msg_recebida = self.recebe()
        print('Msg recebida: ', msg_recebida)

        if msg_recebida.WhichOneof('msg') == 'compra':
           if self.efetua_compra(msg_recebida.compra.ativo, msg_recebida.compra.oferta.quantidade,msg_recebida.compra.oferta.preco, sistema):
            self.envia(self.msg_notif_exec(msg_recebida.compra.ativo,msg_recebida.compra.oferta.preco,
                                          msg_recebida.compra.oferta.quantidade,1,1))
           else:
               self.envia(self.msg_resposta(0)) #msg de falha

        elif msg_recebida.WhichOneof('msg') == 'venda':
            if self.efetua_venda(msg_recebida.venda.ativo, msg_recebida.venda.oferta.quantidade,msg_recebida.venda.oferta.preco, sistema):
                self.envia(self.msg_notif_exec(msg_recebida.venda.ativo, msg_recebida.venda.oferta.preco,
                                              msg_recebida.venda.oferta.quantidade, 2, 1))
            else:
                self.envia(self.msg_resposta(0))

        elif msg_recebida.WhichOneof('msg') == 'cancela_venda':
            try:
                ordem = self.efetua_cancelamento_venda(msg_recebida.cancela_venda.ativo)
                self.envia(self.msg_notif_exec(ordem.ativo, ordem.preco, ordem.num, 2, 1))
            except BaseException as e:
                self.envia(self.msg_resposta(0))

        elif msg_recebida.WhichOneof('msg') == 'cancela_compra':
            try:
                ordem = self.efetua_cancelamento_compra(msg_recebida.cancela_compra.ativo)
                self.envia(self.msg_notif_exec(ordem.ativo, ordem.preco, ordem.num, 1, 1))
            except BaseException as e:
                self.envia(self.msg_resposta(0))

        elif msg_recebida.WhichOneof('msg') == 'info':
            try:
                ativo = sistema.info(msg_recebida.info.ativo)
                msg = self.msg_notif_info(ativo)
                print(ativo)
                print('msg proto info', msg)
            except BaseException as e:
                print(str(e))
                self.envia(self.msg_resposta(0))

        elif msg_recebida.WhichOneof('msg') == 'autenticacao':
               if self.autenticacao(msg_recebida.autenticacao.usuario,
                msg_recebida.autenticacao.senha):  # Se se autenticou com sucesso, envia msg de sucesso status = 1
                   self.envia(self.msg_resposta(1))
                   self.estado = Estado.AUTENTICADO
               else: # Se não conseguiu autenticar com sucesso, envia msg de erro status = 0
                   self.envia(self.msg_resposta(0))

        elif msg_recebida.WhichOneof('msg') == 'saida':
            if self.encerra_conexao():
                self.socket.shutdown(SHUT_RDWR)

    def efetua_compra(self, ativo, quantidade, preco, sistema):
        try:
            o = Ordem(ativo=ativo, preco=preco, num=quantidade, usuario=self.usuario_autenticado)
            resultado = sistema.lanca_ordem(o)
            lista_ordens.append(resultado)
            return True
        except:
            return False

    def efetua_venda(self, ativo, quantidade, preco, sistema):
        try:
            o = Ordem(ativo=ativo, preco=preco,
                      compra=False, num=quantidade, usuario=self.usuario_autenticado)
            resultado = sistema.lanca_ordem(o)
            lista_ordens.append(resultado)
            return True
        except:
            return False

    def efetua_cancelamento_compra(self, ativo):
        ordem = ''
        atv = sistema._obtem_ativo(ativo)
        for o in atv.compras:
            if o.ativo == ativo.nome:
                ordem = o
                break
        sistema.cancela(ordem)
        return ordem

    def efetua_cancelamento_venda(self, ativo):
        ordem = ''
        ativo = sistema._obtem_ativo(ativo)
        for o in ativo.vendas:
            if o.ativo == ativo.nome:
                ordem = o
                break
        sistema.cancela(ordem)
        return ordem

    def encerra_conexao(self):
        self.estado = Estado.DESCONECTADO
        return True

    def autenticacao(self, msg_usuario, msg_senha):
        usuario = msg_usuario
        senha = msg_senha
        b = False
        for chave, valor in usuarios.items():
            if chave == usuario and valor == senha:
                self.usuario_autenticado = usuario
                b = True
                break
        return b

class BaseServer(Protocolo_Mensagens):

    def __init__(self, porta: int):
        Protocolo_Mensagens.__init__(self, porta)
        #self.porta = porta
        self.socket.listen(2)

    def recebece_conexoes(self):
        sock, addr = self.socket.accept()
        return ServidorProtocolo(sock)

if __name__ == "__main__":
    print("Iniciando servidor...")
    sistema = Sistema()
    servidor_protocolo = BaseServer(5000)

    while True:
        conn = servidor_protocolo.recebece_conexoes()
        while not conn.estado == Estado.DESCONECTADO:
            conn.verifica_msg_comando(sistema)
