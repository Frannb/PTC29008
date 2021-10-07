from enum import Enum
from BaseProto import Protocolo_Mensagens
from socket import *

def menu_inicial():
    print('==========================================================')
    print(''' Olá, seja bem vindo ao sistema que negocia ativos, \n
                para iniciar realize a autenticação.''')
    print('==========================================================')
    usuario = input('Digite seu login: ')
    senha = input('Digite sua senha: ')
    return usuario, senha

def menu_opcoes():
    opcao = int(input('''Selecione uma opção:
        1. Compra de Ativo
        2. Venda de Ativo
        3. Cancelamento de Ordem (compra ou venda de ativos)
        4. Informações do ativo
        0. Sair
        Opção: '''))
    return opcao


class Estado(Enum):
    NOAUTH = 1
    AUTH = 2

class ClienteProtocolo(Protocolo_Mensagens):
    def __init__(self, host: str, port: int):
        Protocolo_Mensagens.__init__(self)
        self.socket.connect((host, port))
        self.state = Estado.NOAUTH

    def autentica(self, usuario, senha):
        if self.state == Estado.AUTH: return True  # Cliente já autenticado
        # Faz esse passo o cliente não esteja autenticado
        msg = self.autenticacao(usuario, senha)
        resposta = self.envia_com_resp(msg)
        if resposta.status:
            self.state = Estado.AUTH
            return True
        return False

    def compra_ativo(self, ativo, quantidade, preco):
        if self.state == Estado.NOAUTH:
            raise RuntimeError('Cliente não autenticado')
        else:
            msg = self.compra_msgComando(ativo, quantidade, preco)
            resposta = self.envia_com_resp(msg)
            # servidor vai retornar a resposta
            if resposta.status == 1:
                return resposta
            return False

    # Quando o ativo for vendido não vai ter resposta
    def venda_ativo(self, ativo, quantidade, preco):
        if self.state == Estado.NOAUTH: raise RuntimeError('Cliente não autenticado')
        msg = self.venda_msgComando(ativo, quantidade, preco)
        resposta = self.envia_com_resp(msg)
        # servidor vai retornar a resposta
        if resposta.status == 1:
            return resposta
        return False

    def cancelamento_ordem_venda(self, ativo: str, quantidade: int = 0, preco: int = 0):
        # def cancelamento_ordem_venda(self, ativo, quantidade, preco):
        if self.state == Estado.NOAUTH: raise RuntimeError('Cliente não autenticado')
        msg = self.cancela_venda_msgComando(ativo, quantidade, preco)
        resposta = self.envia_com_resp(msg)
        return resposta

    def cancelamento_ordem_compra(self, ativo: str, quantidade: int = 0, preco: int = 0):
        # def cancelamento_ordem_compra(self, ativo, quantidade, preco):
        if self.state == Estado.NOAUTH: raise RuntimeError('Cliente não autenticado')
        msg = self.cancela_compra_msgComando(ativo, quantidade, preco)
        resposta = self.envia_com_resp(msg)
        return resposta

    def informacao_ativo(self, ativo: str, notificar: bool = False):
        if self.state == Estado.NOAUTH: raise RuntimeError('Cliente não autenticado')
        msg = self.info_msgComando(ativo, notificar)
        resposta = self.envia_com_resp(msg)
        print(resposta.status)
        return resposta

    def sair(self):
        if self.state == Estado.NOAUTH: raise RuntimeError('Cliente não autenticado')
        msg = self.sair_msgComando()
        self.envia(msg)
        self.state = Estado.NOAUTH


if __name__ == '__main__':
    clienteProto = ClienteProtocolo('127.0.0.1', 5000)
    login, senha = menu_inicial()

    resultado = clienteProto.autentica(login, senha)

    if resultado:
        while True:
            opcao = menu_opcoes()
            if opcao == 1:
                # Opção de compra
                nome_ativo = input("Insira o nome do ativo: ")
                preco = int(input("Insira o preço: "))
                quantidade = int(input("Insira a quantidade: "))
                r = clienteProto.compra_ativo(nome_ativo, quantidade, preco)
                if r:
                    print('Compra de ativo realizada!')
                else:
                    print('ERRO: compra não efetivada!')

            elif opcao == 2:
                # Opção de venda
                nome_ativo = input("Insira o nome do ativo: ")
                preco = int(input("Insira o preço: "))
                quantidade = int(input("Insira a quantidade: "))
                r = clienteProto.venda_ativo(nome_ativo, quantidade, preco)
                if r:
                    print('Venda de ativo registrada!')
                else:
                    print('ERRO ao registrar venda!')

            elif opcao == 3:
                # Opção de cancelamento
                subOpcao = int(input('''Selecione uma opção:
                1. Cancelamento de Compra de Ativo
                2. Cancelamento de Venda de Ativo
                0. Sair
                Opção: '''))

                if subOpcao == 1:
                    # mostrar apenas as ordens do usuario
                    ordem_ativo = input("Selecione o número da ordem que deseja cancelar: ")
                    r = clienteProto.cancelamento_ordem_compra(ordem_ativo)
                    if r.status == 1:
                        print('\n Ordem cancelada: \n', r.exec)
                    else:
                        print('ERRO ao cancelar ordem!')

                elif subOpcao == 2:
                    ordem_ativo = input("Selecione o número da ordem que deseja cancelar: ")
                    r = clienteProto.cancelamento_ordem_venda(ordem_ativo)
                    if r.status == 1:
                        print('\n Ordem cancelada: \n', r.exec)
                    else:
                        print('ERRO ao cancelar ordem!')

                elif subOpcao == 0:
                    # Volta para as opções
                    menu_opcoes()

            elif opcao == 4:
                # Informações sobre um ativo
                nome_ativo = input("Informe o nome do Ativo: ")
                clienteProto.informacao_ativo(nome_ativo)


            elif opcao == 0:
                clienteProto.sair()
                print('Saindo...')
                break
