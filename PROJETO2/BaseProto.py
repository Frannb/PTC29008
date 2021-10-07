from socket import *
import mensagem_protocolo_ativo_pb2 as msg_proto


class Protocolo_Mensagens:

    def __init__(self, port:int=0):
        'Inicia o construtor criando um socket'
        self.socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        self.socket.bind(('127.0.0.1', port))

    def envia(self, msg):
        'envia uma mensagem, sem esperar resposta'
        self.socket.send(msg.SerializeToString())

    def envia_com_resp(self, msg):
        'envia uma mensagem de comando, e espera sua resposta'
        self.socket.send(msg.SerializeToString())
        return self.recebe()

    def recebe(self):
        'recebe uma mensagem de rsposta'
        data = self.socket.recv(8192)
        msg_protocolo = msg_proto.MsgResp()
        msg_protocolo.ParseFromString(data)
        return msg_protocolo

    def compra_msgComando(self, ativo, quantidade, preco):
        msg = msg_proto.MsgComando()
        msg.compra.ativo = ativo
        msg.compra.oferta.quantidade = quantidade
        msg.compra.oferta.preco = preco
        return msg

    def venda_msgComando(self, ativo, quantidade, preco):
        msg = msg_proto.MsgComando()
        msg.venda.ativo = ativo
        msg.venda.oferta.quantidade = quantidade
        msg.venda.oferta.preco = preco
        return msg

    def cancela_venda_msgComando(self, ativo, quantidade, preco):
        msg = msg_proto.MsgComando()
        msg.cancela_venda.ativo = ativo
        msg.cancela_venda.oferta.quantidade = quantidade
        msg.cancela_venda.oferta.preco = preco
        return msg

    def cancela_compra_msgComando(self, ativo, quantidade, preco):
        msg = msg_proto.MsgComando()
        msg.cancela_compra.ativo = ativo
        msg.cancela_compra.oferta.quantidade = quantidade
        msg.cancela_compra.oferta.preco = preco
        return msg

    def autenticacao(self, usuario, senha):
        msg = msg_proto.MsgComando()
        msg.autenticacao.usuario = usuario
        msg.autenticacao.senha = senha
        return msg

    def info_msgComando(self, ativo: str, notificar: bool = False):
        msg = msg_proto.MsgComando()
        msg.info.ativo = ativo
        msg.info.notificar = notificar
        return msg

    def msg_resposta(self, status):
        msg_resposta = msg_proto.MsgResp()
        msg_resposta.status = status
        return msg_resposta

    def sair_msgComando(self):
        msg = msg_proto.MsgComando()
        msg.saida = True
        return msg

    # def msg_notif_info(self, ativo, ultimo_preco, compras, vendas, status):
    #     msg = msg_proto.MsgResp()
    #     msg.status = status
    #     msg.info.ativo = ativo
    #     msg.info.ultimo_preco = ultimo_preco
    #     msg.info.compras = compras
    #     msg.info.vendas = vendas
    #     return msg

    def msg_notif_exec(self, ativo, preco, quantidade, tipo, status):
        msg = msg_proto.MsgResp()
        msg.status = status
        msg.exec.ativo = ativo
        msg.exec.preco = preco
        msg.exec.quantidade = quantidade
        msg.exec.tipo = tipo
        return msg

    def oferta(self, preco, quantidade):
        msg = msg_proto.Oferta()
        msg.preco = preco
        msg.quantidade = quantidade
        return msg

    def msg_notif_info(self, ativo):
        msg = msg_proto.MsgResp()
        compras_ativo = []
        vendas_ativo = []
        for ordem in ativo.compras:
            oferta = self.oferta(ordem.preco, ordem.num)
            compras_ativo.append(oferta)
        for ordem in ativo.vendas:
            oferta = self.oferta(ordem.preco, ordem.num)
            vendas_ativo.append(oferta)
        print(compras_ativo)
        print(vendas_ativo)
        msg.status = 1
        msg.info.ativo = ativo.nome
        msg.info.ultimo_preco = ativo.cotacao
        if len(compras_ativo) > 1:
            msg.info.compras.extend([compras_ativo])
        else:
            msg.info.compras.append(None)
        if len(vendas_ativo > 1):
            msg.info.vendas.extend([vendas_ativo])
        else:
            msg.info.venda.append(None)
        return msg
