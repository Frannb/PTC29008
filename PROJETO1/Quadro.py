class Quadro:
    def set_bit(self, dado, pos):  # Acende o bit na posição
        mascara = (1 << pos)
        return dado | mascara

    def clear_bit(self, dado, pos):  # Apaga o bit na posição
        mascara = ~(1 << pos)
        return dado & mascara

    def get_bit(self, dado, pos):  # Pega o bit na posição
        mascara = (1 << pos)
        return (dado & mascara) >> pos

    def __init__(self, array_bytes=None):
        if array_bytes is None:
            self.controle = 0
            self.sessao = 3
            self.id_proto = 0
            self.dados = b''  # ocupa 1024 bytes
            self.fcs = b''  # ocupa 2 bytes [1 byte LSB e outro MSB]
        else:
            self.controle = array_bytes[0]
            self.sessao = array_bytes[1]
            self.id_proto = array_bytes[2]
            self.dados = bytes(array_bytes[3:-2])
            self.fcs = bytes(array_bytes[-2:])  ##pega os dois últimos dados do array até o final

    # uma opção para setter e getter do tipo de quadro
    def set_data(self):
        # DATA: bit7 = 0
        self.controle = self.clear_bit(self.controle, 7)

    def set_ack(self):
        # ACK: bit7 = 1
        self.controle = self.set_bit(self.controle, 7)

    def is_data(self):
        return self.get_bit(self.controle, 7) == 0

    def is_ack(self):
        return self.get_bit(self.controle, 7)

    def set_sequencia(self, sequencia):
        if sequencia == 0:
            self.controle = self.clear_bit(self.controle, 3)
        else:
            self.controle = self.set_bit(self.controle, 3)

    def get_sequencia(self):
        return self.get_bit(self.controle, 3)

    '''Campo de sessão'''

    def set_sessao(self, num_sessao):
        self.sessao = num_sessao

    def get_sessao(self):
        return self.sessao

    '''Contém o tipo de conteúdo transportado pelo quadro'''

    def set_id_proto(self, id_proto):
        # FIXME se o quadro é um quadro de dados então id proto 11111111
        self.id_proto = id_proto

    def get_id_proto(self):
        return self.id_proto

    '''Contém dado do quadro'''

    def set_dados(self, dados):
        self.dados = dados

    def get_dados(self):
        return self.dados

    '''Contém o valor do código CRC-16-CCITT'''

    def set_fsc(self, fcs):
        self.fcs = fcs

    def get_fsc(self):
        return self.fcs

    def limpa_quadro(self):
        self.controle = 0
        self.sessao = 0
        self.id_proto = 0
        self.dados = b''
        self.fcs = b''

    '''Pega o quadro e o transforma em um array de bytes'''

    def quadro_em_bytes(self):
        array_bytes = bytearray()
        array_bytes.append(self.controle)
        array_bytes.append(self.sessao)
        array_bytes.append(self.id_proto)
        array_bytes += self.dados
        array_bytes += self.fcs
        return bytes(array_bytes)