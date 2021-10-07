from Subcamada import Subcamada
from Quadro import Quadro
import crc

class Enquadramento(Subcamada):
    esc = 0x7d      # Caractere de escape = 01111101 = } = 7d
    flag = 0x7e     # Caractere de flag   = 01111110 = ~ = 7e
    escXOR = 0x5d   # ESC xor 20 = ] = 5d
    flagXOR = 0x5e  # FLAG  xor 20 = ^ = 5e
    contador  = 0

    def __init__(self, porta, tout):
        Subcamada.__init__(self, porta, tout)
        self.estados = ["Ocioso", "Escape", "Recebendo"]
        self.estado_atual = self.estados[0]
        self.porta = porta
        self.quadro_recebido = bytearray()
        self.quadro_correto = False
        self.disable_timeout()

    #FIXME Neste método verifica se no dado existe uma flag ou um esc, caso exista uma flag será
    # adiciona um esc([) e depois será feito xorFLAG. E se o dado for uma esc, ocorrerá da mesma
    # forma, será adiciona um es([), e após um xorESC
    def enquadra(self, msg):
        frame = bytearray()
        # adiciona a flag INICIAL ao frame
        frame.append(Enquadramento.flag)
        for dado in msg:
            if dado == Enquadramento.flag:
                frame.append(Enquadramento.esc)
                frame.append(Enquadramento.flagXOR)  # ESC xor FLAG = 00000011 = 5e
            elif dado == Enquadramento.esc:
                frame.append(Enquadramento.esc)
                frame.append(Enquadramento.escXOR)  # ESC xor ESC  = 00000000 = 5d
            else:
                frame.append(dado)
        frame.append(Enquadramento.flag) # adiciona a flag FINAL a frame
        return bytes(frame)

    # FIXME Monitora quadros que chegam da serial e chama a MEF com o byte de parametro
    def handle(self):
        byte = self.porta.read(1)
        self.mef(byte)

    def handle_timeout(self):
        self.mef()

    #FIXME Após receber o dado da porta serial (método handle), desencapsula este dado
    # através da mef, e retorna a msg do quadro pra camada superior
    def mef(self, byte=None):
        self.enable_timeout()  # habilita o timeout
        if (byte == None):  # Se ocorre um timeout
            self.quadro_correto = False
            self.quadro_recebido.clear()
            self.estado_atual = self.estados[0]
            self.reload_timeout()
        else:
            for bit in byte:
                #FIXME ESTADO OCIOSO: Neste estado o timeout é desabilitado, e fica aguardando
                # o recebimento de uma flag. Quando receber a flag o estado muda para RECEBENDO
                # e o timeout é habilitado
                if self.estado_atual == self.estados[0]:  # Estado Ocioso
                    self.disable_timeout()
                    if bit == Enquadramento.flag:
                        self.enable_timeout()  # habilita o timeout
                        self.estado_atual = self.estados[2]

                #FIXME ESTADO RECEBENDO: Se o estado atual for o estado RECEBENDO, e o bit for uma
                # flag, isso quer dizer, que já foi recebido todos os dados, e o estado volta
                # para OCIOSO.
                # E se caso o bit for um esc, vai para o estado de ESCAPE.
                # E se não for nem flag e nem esc, continua recebendo o dado e adiciona o dado ao quadro.
                elif self.estado_atual == self.estados[2]:  # estado Recebendo
                    self.reload_timeout()
                    if bit == Enquadramento.flag:
                        self.estado_atual = self.estados[0]
                        self.quadro_correto = True
                        self.envia_superior()
                    elif bit == Enquadramento.esc:
                        self.estado_atual = self.estados[1]
                    else:
                        self.estado_atual = self.estados[2]
                        self.quadro_recebido.append(bit)
                        Enquadramento.contador += 1
                        if(Enquadramento.contador > 1024):
                            self.quadro_recebido.clear()
                            self.estado_atual = self.estados[0]
                            print("Excedeu o tamanho do payload!")


                #FIXME ESTADO ESCAPE: Neste estado será verificado se o bit recebido, caso seja (flag xor 20), o bit
                # é uma flag(~). E se o bit recebido for (esc xor 20), o bit é um esc(])
                # E se caso receber uma flag ou esc como dado, é um erro ocorrido, então o quadro será descartado
                else:  # estado Escape
                    self.reload_timeout()
                    if bit == Enquadramento.flagXOR:
                        self.quadro_recebido.append(Enquadramento.flag)
                        self.estado_atual = self.estados[2]
                    elif bit == Enquadramento.escXOR:
                        self.quadro_recebido.append(Enquadramento.esc)
                        self.estado_atual = self.estados[2]
                    elif bit == Enquadramento.flag or bit == Enquadramento.esc:  # Verificando se ocorreu um erro no quadro.
                        self.quadro_correto = False
                        self.quadro_recebido.clear()
                        self.envia_superior()
                        self.estado_atual = self.estados[0]

    #FIXME envia o dado da mef para a subcamada superior, no caso aplicação
    def envia_superior(self):
        if self.quadro_correto:
            if (self.verifica_crc(bytes(self.quadro_recebido))):
                quadro = Quadro(self.quadro_recebido)
                self.upper.recebe(quadro)
                self.quadro_correto = False
                self.quadro_recebido.clear()
        else:
            self.upper.recebe("Erro ao receber quadro")

    #FIXME Recebe o dado da serial vindo da subcamada superior, enquadra e retorna pra serial
    def envia(self, quadro):
        #print("Recebeu um quadro tipo ", quadro.get_tipo_quadro())
        array_quadro = quadro.quadro_em_bytes()  # quadro recebido da camada superior sem o
        quadro_crc = self.adiciona_crc(array_quadro)  # adiciona o crc ao quadro_
        quadro_enquadrado = self.enquadra(quadro_crc)  # envia pro enquadramento
        self.porta.write(quadro_enquadrado)  # escreve na porta serial
        quadro.limpa_quadro()

    def recebe(self):
        pass

    '''Adiciona dois bytes de verificaçao ao dado transmitido'''
    def adiciona_crc(self, dado):
        fcs = crc.CRC16()  # instância do obj crc
        fcs.update(dado)  # insere mais um byte de verificação
        dado_crc = fcs.gen_crc()  # gera o crc
        return dado_crc

    '''Faz a verificação de quadro corrompido'''
    def verifica_crc(self, quadro):
        fcs = crc.CRC16()
        fcs.update(quadro)
        return fcs.check_crc()
